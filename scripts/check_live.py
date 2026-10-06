#!/usr/bin/env python3
"""Check that blog posts are really live before sharing them on social media.

Run this before scheduling or publishing a Zernio (or any social) post that
links to the site. For each post it checks the live page, not the repo:

  - the URL answers 200 (after redirects) and is the post, not the 404 page
  - the page is not noindex and its canonical URL is the post's own URL
  - og:title is set and og:image loads as an image (the link preview)
  - the URL is listed in the live sitemap.xml

A post's `date` is Central time (`timezone` in _config.yml). The site
rebuilds at five past every hour, so a post dated 08:00 is live by about
09:15; schedule social shares after that, and run this check first.

Usage (standard library only):
  python3 scripts/check_live.py _posts/2026-10-07-how-to-build-....md
  python3 scripts/check_live.py https://katieallred.com/nonprofit-website-with-divi/
  python3 scripts/check_live.py --date 2026-10-07   # every post dated that day
  python3 scripts/check_live.py --recent 14          # posts from the last 14 days

Exits 1 if any post is not live or its link preview is broken.
"""
import argparse
import datetime as dt
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://katieallred.com"
USER_AGENT = "katieallred.com live check"
REBUILD_LAG = dt.timedelta(minutes=75)  # hourly rebuild at :05 plus build time


class Head(HTMLParser):
    """Collect <title>, <link rel=canonical> and <meta> tags."""

    def __init__(self):
        super().__init__()
        self.meta, self.canonical, self.title, self._in_title = {}, "", "", False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("property") or a.get("name")
            if key and key not in self.meta:
                self.meta[key] = a.get("content") or ""
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href") or ""
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read() if method == "GET" else b""
            return resp.status, resp.geturl(), resp.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as err:
        return err.code, url, err.headers.get("Content-Type", ""), b""


def same_page(a, b):
    """Compare URLs ignoring scheme, www. and a trailing slash."""
    def norm(u):
        p = urlsplit(u)
        return (p.netloc.lower().removeprefix("www."), p.path.rstrip("/") or "/")
    return norm(a) == norm(b)


def front_matter(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "-")):
            fm[k.strip()] = v.strip().strip("'\"")
    return fm


def post_date(fm, path):
    raw = fm.get("date") or Path(path).name[:10]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(raw[:19], fmt)
        except ValueError:
            continue
    return None


def central_now():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).replace(tzinfo=None)
    except Exception:  # no tz database: fall back to UTC-5
        return dt.datetime.utcnow() - dt.timedelta(hours=5)


def posts_between(start, end):
    """Post files whose date falls in [start, end] (dates, Central time)."""
    found = []
    for path in sorted((ROOT / "_posts").glob("*.md")):
        d = post_date(front_matter(path), path)
        if d and start <= d.date() <= end:
            found.append(path)
    return found


def check(url, sitemap, label=None, when=None):
    problems = []
    status, final, ctype, body = fetch(url)
    if status != 200:
        problems.append(f"page answered {status}")
    elif "html" not in ctype:
        problems.append(f"page is {ctype}, not HTML")
    else:
        head = Head()
        head.feed(body.decode("utf-8", "replace"))
        if "page not found" in head.title.lower() or "404" in head.title:
            problems.append(f"served the 404 page ({head.title.strip()!r})")
        if not same_page(final, url):
            problems.append(f"redirected to {final}")
        if "noindex" in head.meta.get("robots", ""):
            problems.append("page is noindex")
        if not head.canonical:
            problems.append("no canonical URL")
        elif not same_page(head.canonical, url):
            problems.append(f"canonical points to {head.canonical}")
        if not head.meta.get("og:title"):
            problems.append("no og:title (link preview will be bare)")
        image = head.meta.get("og:image")
        if not image:
            problems.append("no og:image (link preview has no picture)")
        else:
            istatus, _, itype, _ = fetch(urljoin(final, image))
            if istatus != 200 or not itype.startswith("image/"):
                problems.append(f"og:image {image} answered {istatus} {itype}")
    if sitemap is not None and not any(same_page(u, url) for u in sitemap):
        problems.append("not in the live sitemap.xml")

    name = label or url
    if problems:
        print(f"NOT READY  {name}\n           {url}")
        if when:
            print(f"           post date {when:%Y-%m-%d %H:%M} Central; "
                  f"expect it live after {when + REBUILD_LAG:%Y-%m-%d %H:%M} Central")
        for p in problems:
            print(f"           - {p}")
        return False
    print(f"LIVE       {name}\n           {url}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("targets", nargs="*", help="post files or live URLs")
    ap.add_argument("--date", help="check every post dated YYYY-MM-DD")
    ap.add_argument("--recent", type=int, metavar="DAYS",
                    help="check posts dated in the last DAYS days")
    ap.add_argument("--site", default=SITE, help=f"live site (default {SITE})")
    args = ap.parse_args()

    jobs = []  # (url, label, post date)
    files = [Path(t) for t in args.targets if not t.startswith("http")]
    if args.date:
        day = dt.date.fromisoformat(args.date)
        files += posts_between(day, day)
    if args.recent:
        today = central_now().date()
        files += posts_between(today - dt.timedelta(days=args.recent), today)
    for path in files:
        fm = front_matter(path)
        if not fm.get("permalink"):
            print(f"SKIP       {path}: no permalink in front matter")
            continue
        jobs.append((args.site.rstrip("/") + fm["permalink"], fm.get("title"),
                     post_date(fm, path)))
    jobs += [(t, None, None) for t in args.targets if t.startswith("http")]
    if not jobs:
        ap.error("give post files, URLs, --date or --recent")

    status, _, _, body = fetch(args.site.rstrip("/") + "/sitemap.xml")
    sitemap = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body.decode()) if status == 200 else None
    if sitemap is None:
        print(f"warning: live sitemap answered {status}; skipping that check")

    results = [check(url, sitemap, label, when) for url, label, when in jobs]
    print(f"\n{sum(results)} of {len(results)} live.")
    if not all(results):
        print("Don't share the NOT READY posts yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
