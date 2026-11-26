"""
Ops Radar news collector.

Reads feeds.json, pulls each region's RSS feeds, keeps logistics/ops headlines,
removes duplicates and writes data/news.json for the website's Ops Radar page.

Uses only Python's standard library, so there is nothing to install.
Run it yourself:      python scripts/collect_news.py
GitHub runs it daily: .github/workflows/collect-news.yml
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
FEEDS_FILE = ROOT / "feeds.json"
OUT_FILE = ROOT / "data" / "news.json"
USER_AGENT = "Mozilla/5.0 (compatible; OpsRadar/1.0)"


def fetch(url: str) -> bytes:
    if url.startswith("file://"):
        return Path(url[7:]).read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return ""


def parse_feed(raw: bytes):
    """Yields dicts from RSS 2.0 or Atom."""
    root = ET.fromstring(raw)
    atom = "{http://www.w3.org/2005/Atom}"
    for item in root.iter("item"):
        title = clean(item.findtext("title"))
        source_el = item.find("source")
        source = clean(source_el.text) if source_el is not None else ""
        # Google News puts " - Source" at the end of the title
        if source and title.endswith(" - " + source):
            title = title[: -len(" - " + source)]
        yield {
            "title": title,
            "link": (item.findtext("link") or "").strip(),
            "source": source,
            "published": parse_date(item.findtext("pubDate") or ""),
        }
    for entry in root.iter(atom + "entry"):
        link_el = entry.find(atom + "link")
        yield {
            "title": clean(entry.findtext(atom + "title")),
            "link": link_el.get("href", "") if link_el is not None else "",
            "source": "",
            "published": parse_date(entry.findtext(atom + "updated") or ""),
        }


def matches(title: str, keywords) -> bool:
    t = title.lower()
    return any(k in t for k in keywords)


def main() -> int:
    cfg = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    keywords = [k.lower() for k in cfg.get("keywords", [])]
    limit = int(cfg.get("max_items_per_region", 12))
    seen_titles = set()
    regions_out = {}
    errors = []

    for region, urls in cfg["regions"].items():
        items = []
        for url in urls:
            try:
                for it in parse_feed(fetch(url)):
                    key = re.sub(r"\W+", "", it["title"].lower())[:80]
                    if not it["title"] or not it["link"] or key in seen_titles:
                        continue
                    if keywords and not matches(it["title"], keywords):
                        continue
                    seen_titles.add(key)
                    items.append(it)
            except Exception as exc:  # one bad feed must not stop the rest
                errors.append(f"{region}: {url[:80]} -> {exc}")
        items.sort(key=lambda x: x["published"], reverse=True)
        regions_out[region] = items[:limit]
        print(f"{region}: {len(regions_out[region])} items")

    total = sum(len(v) for v in regions_out.values())
    if total == 0 and OUT_FILE.exists():
        print("No items fetched; keeping the previous news.json.")
        for e in errors:
            print("  error:", e)
        return 0

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "regions": regions_out,
        "errors": errors,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {total} items to {OUT_FILE.relative_to(ROOT)}")
    for e in errors:
        print("  error:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
