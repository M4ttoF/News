"""Daily article fetcher for the News vault.

Drives a real Firefox (so content-access extensions run) via Selenium,
collects article links from each source's index page, extracts article
content with Mozilla Readability, and writes clipper-style markdown files
into raw/. Dedupes across runs via state/seen.json.

Usage:
  py scripts/fetch_articles.py              # normal daily run
  py scripts/fetch_articles.py --dry-run    # list new article links, fetch nothing
  py scripts/fetch_articles.py --limit 3    # attempt at most 3 articles (testing)
  py scripts/fetch_articles.py --headless   # force headless regardless of config
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
    driver.get(source["index_url"])
    time.sleep(wait_s)
    result = driver.execute_script("""
        const scope = arguments[0];
        let anchors = [];
        if (scope) anchors = document.querySelectorAll(scope + ' a[href]');
        const fellBack = !anchors.length;
        if (fellBack) anchors = document.querySelectorAll('a[href]');
        return {hrefs: Array.from(anchors).map(a => a.getAttribute('href')),
                fellBack: fellBack && !!scope};
    """, source.get("link_scope_selector"))
    if result["fellBack"]:
        print(f"  WARNING: scope selector {source['link_scope_selector']!r} matched nothing; "
              "using all page links (selector may need updating)")
    hrefs = result["hrefs"]
    pattern = re.compile(source["href_pattern"])
    paths = []
    for href in hrefs:
        if not href or not pattern.search(href):
            continue
        path = href.split("?")[0].split("#")[0]
        if path not in paths:
            paths.append(path)
    return paths


def is_paywalled(article, markers):
    content = article.get("content") or ""
    return any(m in content for m in markers)


def extract_article(driver, url, timeout_s, min_chars, paywall_markers):
    """Navigate and poll until Readability yields a full, non-paywalled article.

    Keeps polling past a paywall barrier because the content-access extension
    may replace it after initial load. Returns the best attempt (or None).
    """
    driver.get(url)
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
            if result["length"] >= min_chars and not is_paywalled(result, paywall_markers):
                return result
            if best is None or rank(result) > rank(best):
                best = result
    return best


def sanitize_filename(title, max_len=80):
    name = re.sub(r'[<>:"/\\|?*\[\]#^]', "", title).strip().rstrip(".")
    name = re.sub(r"\s+", " ", name)
    return name[:max_len].strip()


def parse_published(raw):
    if not raw:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    return m.group(1) if m else None


def write_raw_file(cfg, source, url, article):
    raw_dir = Path(cfg["vault"]) / cfg["raw_dir"]
    raw_dir.mkdir(parents=True, exist_ok=True)

    published = parse_published(article.get("published")) or date.today().isoformat()
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
        "---",
    ])
    path.write_text(f"{frontmatter}\n\n# {title}\n\n{body}\n", encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description="Fetch new articles into raw/")
    ap.add_argument("--dry-run", action="store_true", help="list new links, fetch nothing")
    ap.add_argument("--limit", type=int, default=0, help="max articles to attempt this run")
    ap.add_argument("--headless", action="store_true", help="force headless mode")
    args = ap.parse_args()

    cfg = load_config()
    seen = load_seen()
    headless = args.headless or cfg.get("headless", False)
    fetched, failed, skipped = [], [], 0

    driver = make_driver(cfg, headless)
    try:
        for source in cfg["sources"]:
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

                if (article and article["length"] >= cfg["min_article_chars"]
                        and not is_paywalled(article, markers)):
                    path = write_raw_file(cfg, source, url, article)
                    entry.update(status="fetched", date=date.today().isoformat(),
                                 file=path.name)
                    fetched.append(path.name)
                    print(f"  OK ({article['length']} chars) -> {path.name}")
                else:
                    got = article["length"] if article else 0
                    why = "PAYWALLED" if article and is_paywalled(article, markers) else "TOO SHORT"
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
