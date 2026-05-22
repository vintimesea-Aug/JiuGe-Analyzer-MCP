"""Fetch podcast episode metadata from Xiaoyuzhou via web scraping."""

import json
import re
from urllib.request import Request, urlopen
from urllib.error import URLError


class FetchError(Exception):
    """Failed to fetch episode data."""


def parse_episode_id(url: str) -> str:
    m = re.search(r"episode/([a-zA-Z0-9]+)", url)
    if not m:
        raise FetchError(f"Cannot parse episode_id from URL: {url}")
    return m.group(1)


def fetch_episode_detail(episode_id: str) -> dict:
    """Scrape episode metadata from Xiaoyuzhou public page."""
    url = f"https://www.xiaoyuzhoufm.com/episode/{episode_id}"
    req = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        raise FetchError(f"Page fetch failed: {e}")

    meta = {"episode_id": episode_id, "title": episode_id, "podcast_name": "", "host": "", "audio_url": ""}

    # schema.org JSON-LD
    m = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        ld = json.loads(m.group(1))
        meta["title"] = ld.get("name", episode_id)
        meta["description"] = ld.get("description", "")
        dur = ld.get("timeRequired", "")
        if dur.startswith("PT"):
            meta["duration"] = dur[2:-1] if dur.endswith("M") else dur[2:]
        media = ld.get("associatedMedia", {})
        if isinstance(media, dict):
            meta["audio_url"] = media.get("contentUrl", "")
        series = ld.get("partOfSeries", {})
        if isinstance(series, dict):
            meta["podcast_name"] = series.get("name", "")
        meta["pubDate"] = ld.get("datePublished", "")

    # __NEXT_DATA__ is richer
    m2 = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m2:
        nd = json.loads(m2.group(1))
        ep = nd.get("props", {}).get("pageProps", {}).get("episode", {})
        if ep:
            meta["title"] = ep.get("title", meta["title"])
            meta["podcast_name"] = ep.get("podcast", {}).get("title", meta["podcast_name"])
            meta["host"] = ep.get("podcast", {}).get("author", "")
            meta["duration"] = ep.get("duration", meta.get("duration", ""))
            meta["pubDate"] = ep.get("pubDate", meta.get("pubDate", ""))
            meta["playCount"] = ep.get("playCount", 0)
            meta["commentCount"] = ep.get("commentCount", 0)
            meta["clapCount"] = ep.get("clapCount", 0)
            meta["favoriteCount"] = ep.get("favoriteCount", 0)
            meta["description"] = ep.get("description", meta.get("description", ""))
            enclosure = ep.get("enclosure", {})
            if isinstance(enclosure, dict):
                meta["audio_url"] = enclosure.get("url", meta["audio_url"])

    return meta
