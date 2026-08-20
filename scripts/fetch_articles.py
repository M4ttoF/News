"""Daily article fetcher for the News vault.

Drives a real Firefox (so content-access extensions run) via Selenium,
collects article links from each source's index page, extracts article
content with Mozilla Readability, and writes clipper-style markdown files
into raw/. Dedupes across runs via state/seen.json.

When an article still reads as paywalled after the extension has had its
chance, the run falls back to an archive.today snapshot in a second tab.
archive.today gates some sessions behind a security check; the script never
answers one itself - it pauses and asks you to tick the box in the Firefox
window, then carries on. Solve it once and the profile cookie usually covers
the rest of the run. Not every article has a snapshot; those are reported and
skipped as before.

Usage:
  uv run scripts/fetch_articles.py              # normal daily run
  uv run scripts/fetch_articles.py --dry-run    # list new article links, fetch nothing
  uv run scripts/fetch_articles.py --limit 3    # attempt at most 3 articles (testing)
  uv run scripts/fetch_articles.py --headless   # force headless regardless of config
"""

import argparse
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

from markdownify import markdownify
from selenium import webdriver

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
SEEN_PATH = SCRIPT_DIR / "state" / "seen.json"
READABILITY_JS = (SCRIPT_DIR / "readability.js").read_text(encoding="utf-8")

EXTRACT_JS = READABILITY_JS + """
try {
  var article = new Readability(document.cloneNode(true)).parse();
  if (!article) return null;
  var published = article.publishedTime;
  if (!published) {
    var meta = document.querySelector('meta[property="article:published_time"], meta[name="article:published_time"]');
    if (meta) published = meta.getAttribute('content');
  }
  return {
    title: article.title,
    byline: article.byline,
    published: published,
    content: article.content,
    length: article.length
  };
} catch (e) {
  return null;
}
"""


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_seen():
    if SEEN_PATH.exists():
        return json.loads(SEEN_PATH.read_text(encoding="utf-8"))
    return {}


def save_seen(seen):
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEN_PATH.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def make_driver(cfg, headless):
    options = webdriver.FirefoxOptions()
    options.binary_location = cfg["firefox_binary"]
    profile = cfg.get("firefox_profile", "")
    if profile:
        if not Path(profile).is_dir():
            sys.exit(f"firefox_profile does not exist: {profile}\n"
                     "Create it via about:profiles (see scripts/SETUP.md) and put its path in config.json.")
        options.add_argument("-profile")
        options.add_argument(profile)
    else:
        print("WARNING: no firefox_profile configured - using a fresh temp profile (no extensions).")
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(60)
    return driver


def collect_links(driver, source, wait_s):
    """Return article paths from the source's index page.

    A source may set "title_pattern" (case-insensitive regex): only links whose
    teaser text matches are kept - used to hold topical pages like /world to a
    subset of subjects. Text is pooled per path first, since one article can
    appear as several teasers (some of them image links with no text).
    """
    driver.get(source["index_url"])
    time.sleep(wait_s)
    result = driver.execute_script("""
        const scope = arguments[0];
        let anchors = [];
        if (scope) anchors = document.querySelectorAll(scope + ' a[href]');
        const fellBack = !anchors.length;
        if (fellBack) anchors = document.querySelectorAll('a[href]');
        return {links: Array.from(anchors).map(a => ({href: a.getAttribute('href'),
                                                      text: a.textContent.trim()})),
                fellBack: fellBack && !!scope};
    """, source.get("link_scope_selector"))
    if result["fellBack"]:
        print(f"  WARNING: scope selector {source['link_scope_selector']!r} matched nothing; "
              "using all page links (selector may need updating)")
    pattern = re.compile(source["href_pattern"])
    texts = {}  # path -> pooled teaser text, insertion-ordered
    for link in result["links"]:
        href = link["href"]
        if not href or not pattern.search(href):
            continue
        path = href.split("?")[0].split("#")[0]
        texts[path] = (texts.get(path, "") + " " + link["text"]).strip()

    title_pattern = source.get("title_pattern")
    if not title_pattern:
        return list(texts)
    title_re = re.compile(title_pattern, re.IGNORECASE)
    kept = [path for path, text in texts.items() if title_re.search(text)]
    dropped = len(texts) - len(kept)
    if dropped:
        print(f"  title filter kept {len(kept)}/{len(texts)} links")
    return kept


def is_paywalled(article, markers):
    content = article.get("content") or ""
    return any(m in content for m in markers)


def is_usable(article, min_chars, markers):
    return (bool(article) and article.get("length", 0) >= min_chars
            and not is_paywalled(article, markers))


def poll_readability(driver, timeout_s, min_chars, paywall_markers):
    """Poll Readability on the current page until it yields a usable article.

    Keeps polling past a paywall barrier because the content-access extension
    may replace it after initial load. Returns the best attempt (or None).
    """
    best = None
    deadline = time.monotonic() + timeout_s

    def rank(a):  # non-paywalled beats paywalled, then longer beats shorter
        return (not is_paywalled(a, paywall_markers), a["length"])

    while time.monotonic() < deadline:
        time.sleep(2)
        try:
            result = driver.execute_script(EXTRACT_JS)
        except Exception:
            continue  # page mid-navigation or script blocked; poll again
        if result and result.get("length"):
            if is_usable(result, min_chars, paywall_markers):
                return result
            if best is None or rank(result) > rank(best):
                best = result
    return best


def extract_article(driver, url, timeout_s, min_chars, paywall_markers):
    driver.get(url)
    return poll_readability(driver, timeout_s, min_chars, paywall_markers)


# ---------------------------------------------------------------------------
# archive.today fallback for paywalled articles
# ---------------------------------------------------------------------------

ARCHIVE_HOST_RE = r"^https?://archive\.(today|is|ph|li|vn|md|fo)/"


def page_text(driver):
    try:
        return driver.execute_script(
            "return document.body ? document.body.innerText : ''") or ""
    except Exception:
        return ""


def has_marker(text, markers):
    low = text.lower()
    return any(m.lower() in low for m in markers)


def archive_url_for(driver, acfg, url):
    """Aim at the snapshot the bypass banner points to, else construct the URL.

    The banner the extension injects on a blocked page carries archive.today /
    archive.is links, so reuse its host and follow whichever mirror is live.
    """
    href = None
    try:
        href = driver.execute_script(
            "const re = new RegExp(arguments[0]);"
            "const a = Array.from(document.querySelectorAll('a[href]'))"
            "  .find(a => re.test(a.href));"
            "return a ? a.href : null;", ARCHIVE_HOST_RE)
    except Exception:
        pass
    base = acfg.get("base_url", "https://archive.today")
    if href:
        if url.split("://", 1)[-1] in href:
            return href  # banner already deep-links this article
        scheme, rest = href.split("://", 1)
        base = f"{scheme}://{rest.split('/', 1)[0]}"
    return f"{base.rstrip('/')}/newest/{url}"


def clear_security_check(driver, acfg):
    """Hand the browser to the human if archive.today shows its security check.

    Answering the check automatically is off-limits, so this only detects the
    gate, asks for a click, and waits for the page to move past it.
    """
    markers = acfg.get("captcha_markers", [])
    if not has_marker(page_text(driver), markers):
        return True
    limit = acfg.get("captcha_wait_s", 180)
    print("\a    >>> archive.today is showing a security check.")
    print("    >>> Tick the 'I am not a robot' box in the Firefox window that is already open.")
    print(f"    >>> Waiting up to {limit}s. Solving it once usually covers the rest of the run.")
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        time.sleep(3)
        if not has_marker(page_text(driver), markers):
            print("    security check cleared, continuing")
            time.sleep(acfg.get("load_wait_s", 8))
            return True
    print("    security check not cleared in time; skipping this article")
    return False


def fetch_via_archive(driver, acfg, url, min_chars, markers):
    """Read the archive snapshot in a second tab. Returns (article, archive_url)."""
    target = archive_url_for(driver, acfg, url)
    print(f"    archive fallback -> {target}")
    main = driver.current_window_handle
    driver.switch_to.new_window("tab")
    try:
        driver.get(target)
        time.sleep(acfg.get("load_wait_s", 8))
        if not clear_security_check(driver, acfg):
            return None, None
        if has_marker(page_text(driver), acfg.get("no_snapshot_markers", [])):
            print("    no archived snapshot for this article")
            return None, None
        article = poll_readability(driver, acfg.get("extract_timeout_s", 25),
                                   min_chars, markers)
        landed = driver.current_url
        if not is_usable(article, min_chars, markers):
            got = article["length"] if article else 0
            print(f"    archive snapshot unusable ({got} chars)")
            return None, None
        print(f"    archive OK ({article['length']} chars)")
        return article, landed
    finally:
        driver.close()
        driver.switch_to.window(main)


def original_url_from_archive(driver, fallback):
    """Recover the "Saved from" URL from an archive.today snapshot header."""
    try:
        href = driver.execute_script(r"""
            const header = document.getElementById('HEADER') || document.body;
            const inp = header.querySelector('input[type="text"]');
            if (inp && /^https?:\/\//.test(inp.value)) return inp.value;
            const a = Array.from(header.querySelectorAll('a[href^="http"]'))
              .find(a => !/archive\.(today|is|ph|li|vn|md|fo)/.test(a.host));
            return a ? a.href : null;
        """)
        if href:
            return href.split("?")[0]
    except Exception:
        pass
    return fallback


def fetch_one_url(driver, cfg, acfg, url, outlet):
    """Fetch a single explicit URL. Returns (article, canonical_url, archive_url).

    An archive.today link is opened as-is (pausing for the human if the
    security check appears); anything else goes through the normal
    extract-then-archive-fallback path.
    """
    markers = cfg.get("paywall_markers", [])
    if re.match(ARCHIVE_HOST_RE, url):
        driver.get(url)
        time.sleep(acfg.get("load_wait_s", 8))
        if not clear_security_check(driver, acfg):
            return None, url, None
        article = poll_readability(driver, acfg.get("extract_timeout_s", 25),
                                   cfg["min_article_chars"], markers)
        canonical = original_url_from_archive(driver, url)
        return article, canonical, url

    article = extract_article(driver, url, cfg["article_timeout_s"],
                              cfg["min_article_chars"], markers)
    if is_usable(article, cfg["min_article_chars"], markers):
        return article, url, None
    if acfg.get("enabled", True):
        fallback, archive_url = fetch_via_archive(driver, acfg, url,
                                                  cfg["min_article_chars"], markers)
        if fallback:
            return fallback, url, archive_url
    return article, url, None


def sanitize_filename(title, max_len=80):
    name = re.sub(r'[<>:"/\\|?*\[\]#^]', "", title).strip().rstrip(".")
    name = re.sub(r"\s+", " ", name)
    return name[:max_len].strip()


def parse_published(raw):
    if not raw:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    return m.group(1) if m else None


def write_raw_file(cfg, source, url, article, archive_url=None, fallback_published=None):
    raw_dir = Path(cfg["vault"]) / cfg["raw_dir"]
    raw_dir.mkdir(parents=True, exist_ok=True)

    published = (parse_published(article.get("published"))
                 or parse_published(fallback_published)
                 or date.today().isoformat())
    title = (article.get("title") or "Untitled").strip()
    base = f"{published} {sanitize_filename(title)}"
    path = raw_dir / f"{base}.md"
    n = 2
    while path.exists():
        path = raw_dir / f"{base} ({n}).md"
        n += 1

    body = markdownify(article["content"], heading_style="ATX")
    strip_patterns = [re.compile(p) for p in cfg.get("strip_line_patterns", [])]
    body = "\n".join(line for line in body.splitlines()
                     if not any(p.match(line.strip()) for p in strip_patterns))
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    def yq(s):  # quote a YAML scalar safely
        return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

    frontmatter = "\n".join([
        "---",
        f"title: {yq(title)}",
        f"url: {yq(url)}",
        f"outlet: {yq(source['outlet'])}",
        f"author: {yq(article.get('byline') or '')}",
        f"published: {published}",
        f"clipped: {date.today().isoformat()}",
    ] + ([f"archive_url: {yq(archive_url)}", "via: archive.today"] if archive_url else []) + [
        "---",
    ])
    path.write_text(f"{frontmatter}\n\n# {title}\n\n{body}\n", encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description="Fetch new articles into raw/")
    ap.add_argument("--dry-run", action="store_true", help="list new links, fetch nothing")
    ap.add_argument("--limit", type=int, default=0, help="max articles to attempt this run")
    ap.add_argument("--headless", action="store_true", help="force headless mode")
    ap.add_argument("--no-archive", action="store_true",
                    help="skip the archive.today fallback on paywalled articles")
    ap.add_argument("--source", default="",
                    help="only fetch sources whose name contains this (case-insensitive)")
    ap.add_argument("--url", action="append", default=[], metavar="URL",
                    help="fetch this specific article URL (FT or archive.today link; repeatable). "
                         "Skips index pages entirely.")
    ap.add_argument("--outlet", default="Financial Times",
                    help="outlet name recorded for --url fetches (default: Financial Times)")
    args = ap.parse_args()

    cfg = load_config()
    seen = load_seen()
    headless = args.headless or cfg.get("headless", False)
    acfg = cfg.get("archive", {})
    if args.no_archive:
        acfg = dict(acfg, enabled=False)
    fetched, failed, skipped = [], [], 0

    driver = make_driver(cfg, headless)
    try:
        for url in args.url:
            print(f"== URL fetch: {url}")
            markers = cfg.get("paywall_markers", [])
            source = {"outlet": args.outlet}
            try:
                article, canonical, archive_url = fetch_one_url(driver, cfg, acfg, url, args.outlet)
            except Exception as e:
                print(f"  ERROR {url}: {e}")
                failed.append(url)
                continue
            if is_usable(article, cfg["min_article_chars"], markers):
                path = write_raw_file(cfg, source, canonical, article, archive_url=archive_url)
                m = re.search(r"/content/[a-f0-9-]+", canonical or "")
                if m:
                    seen[m.group(0)] = {"attempts": 1, "status": "fetched",
                                        "date": date.today().isoformat(), "file": path.name,
                                        "via": "archive" if archive_url else "direct"}
                    save_seen(seen)
                fetched.append(path.name)
                via = " via archive.today" if archive_url else ""
                print(f"  OK ({article['length']} chars{via}) -> {path.name}")
            else:
                got = article["length"] if article else 0
                why = "PAYWALLED" if article and is_paywalled(article, markers) else "TOO SHORT"
                print(f"  {why} ({got} chars) {url}")
                failed.append(url)
            time.sleep(cfg["article_delay_s"])

        for source in cfg["sources"] if not args.url else []:
            if args.source and args.source.lower() not in source["name"].lower():
                continue
            print(f"== {source['name']}: {source['index_url']}")
            try:
                paths = collect_links(driver, source, cfg["index_load_wait_s"])
            except Exception as e:
                print(f"  FAILED to load index page: {e}")
                failed.append(source["index_url"])
                continue

            new_paths = []
            for p in paths:
                entry = seen.get(p)
                if entry and (entry.get("status") == "fetched"
                              or entry.get("attempts", 0) >= cfg["max_fetch_attempts"]):
                    skipped += 1
                else:
                    new_paths.append(p)
            print(f"  {len(paths)} article links, {len(new_paths)} new")

            if args.dry_run:
                for p in new_paths:
                    print(f"    {source['base_url']}{p}")
                continue

            attempted = 0
            for p in new_paths:
                if args.limit and attempted >= args.limit:
                    break
                attempted += 1
                url = source["base_url"] + p
                entry = seen.setdefault(p, {"attempts": 0})
                entry["attempts"] += 1
                markers = cfg.get("paywall_markers", [])
                try:
                    article = extract_article(driver, url, cfg["article_timeout_s"],
                                              cfg["min_article_chars"], markers)
                except Exception as e:
                    print(f"  ERROR {url}: {e}")
                    failed.append(url)
                    save_seen(seen)
                    continue

                stub, archive_url = None, None
                if not is_usable(article, cfg["min_article_chars"], markers):
                    stub, article = article, None
                    if not acfg.get("enabled", True):
                        pass
                    elif headless:
                        print("    archive fallback skipped (headless: the security "
                              "check needs a human)")
                    else:
                        try:
                            article, archive_url = fetch_via_archive(
                                driver, acfg, url, cfg["min_article_chars"], markers)
                        except Exception as e:
                            print(f"    archive fallback error: {e}")
                            article, archive_url = None, None

                if is_usable(article, cfg["min_article_chars"], markers):
                    path = write_raw_file(cfg, source, url, article,
                                          archive_url=archive_url,
                                          fallback_published=(stub or {}).get("published"))
                    entry.update(status="fetched", date=date.today().isoformat(),
                                 file=path.name, via="archive" if archive_url else "direct")
                    fetched.append(path.name)
                    via = " via archive.today" if archive_url else ""
                    print(f"  OK ({article['length']} chars{via}) -> {path.name}")
                else:
                    probe = article or stub
                    got = probe["length"] if probe else 0
                    why = "PAYWALLED" if probe and is_paywalled(probe, markers) else "TOO SHORT"
                    print(f"  {why} ({got} chars, attempt {entry['attempts']}"
                          f"/{cfg['max_fetch_attempts']}) {url}")
                    failed.append(url)
                save_seen(seen)
                time.sleep(cfg["article_delay_s"])
    finally:
        driver.quit()

    print("\n== Run summary")
    print(f"  fetched: {len(fetched)}")
    for f in fetched:
        print(f"    {f}")
    print(f"  failed/short: {len(failed)}")
    for f in failed:
        print(f"    {f}")
    print(f"  skipped (already seen): {skipped}")
    if failed and not fetched:
        sys.exit(1)


if __name__ == "__main__":
    main()
