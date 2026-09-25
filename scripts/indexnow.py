#!/usr/bin/env python3
"""Tell search engines which URLs changed, through IndexNow.

IndexNow (https://www.indexnow.org) lets a site ping Bing, Yandex, Naver,
Seznam, Yep and other participating engines the moment a page is added,
updated or deleted, instead of waiting for them to recrawl. One submission
to api.indexnow.org is shared with all of them.

The Pages workflow runs this in two steps around the deploy:

  list    Before deploying, compare the freshly built _site/sitemap.xml with
          the live sitemap and print the URLs that are new, were removed, or
          have a newer <lastmod> (a post or page's last_modified_at). With
          --all, print every URL in the sitemap instead.
  submit  After deploying, post those URLs to IndexNow.

The key is the 32-character hex file at the site root (<key>.txt, which
contains the key itself). IndexNow fetches it to check the submission comes
from the site owner. To rotate it, replace that file with a new one.

Standard library only. Try it locally without submitting:
  bundle exec jekyll build
  python3 scripts/indexnow.py list --site _site \
      --live https://www.katieallred.com/sitemap.xml
"""
import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://api.indexnow.org/indexnow"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
MAX_URLS = 10_000  # per request, from the IndexNow protocol
USER_AGENT = "katieallred.com IndexNow (+https://www.indexnow.org)"


def warn(message):
    """Show a warning in the Actions log without failing the run."""
    print(f"::warning title=IndexNow::{message}", file=sys.stderr)


def parse_sitemap(xml):
    """Map each URL in a sitemap to its <lastmod> ('' when it has none)."""
    urls = {}
    for node in ET.fromstring(xml).findall("sm:url", NS):
        loc = (node.findtext("sm:loc", "", NS) or "").strip()
        if loc:
            urls[loc] = (node.findtext("sm:lastmod", "", NS) or "").strip()
    return urls


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.URLError as err:
        # Until GitHub Pages issues the custom domain's certificate, only
        # http:// works; the sitemap itself is the same either way.
        if url.startswith("https://") and isinstance(err.reason, ssl.SSLError):
            warn(f"HTTPS failed for {url} ({err.reason}); trying http.")
            return fetch("http://" + url[len("https://"):])
        raise


def changed_urls(built, live):
    """URLs that are new, gone, or carry a different <lastmod>."""
    added = [u for u in built if u not in live]
    updated = [u for u in built if u in live and built[u] != live[u]]
    removed = [u for u in live if u not in built]
    return added + updated + removed


def cmd_list(args):
    built = parse_sitemap((Path(args.site) / "sitemap.xml").read_bytes())
    if args.all:
        urls = list(built)
    else:
        try:
            live = parse_sitemap(fetch(args.live))
        except (urllib.error.URLError, ET.ParseError, OSError) as err:
            # Nothing to compare against (first deploy, or the site is
            # down): offer everything once rather than nothing.
            warn(f"Couldn't read the live sitemap ({err}); listing every URL.")
            live = {}
        urls = changed_urls(built, live)
    for url in urls:
        print(url)
    print(f"IndexNow: {len(urls)} changed URL(s).", file=sys.stderr)


def find_key(root):
    for path in sorted(Path(root).glob("*.txt")):
        if re.fullmatch(r"[0-9a-f]{32}", path.stem):
            if path.read_text().strip() == path.stem:
                return path.stem
    return None


def cmd_submit(args):
    urls = [u.strip() for u in Path(args.urls).read_text().splitlines()]
    urls = [u for u in urls if u]
    if not urls:
        print("IndexNow: nothing changed, nothing to submit.")
        return

    key = find_key(args.key_dir)
    if not key:
        warn(f"No <key>.txt key file found in {args.key_dir}; skipping.")
        return

    site_url = args.site_url.rstrip("/")
    host = urlsplit(site_url).hostname
    # Only URLs on this host and under the key file's folder are accepted.
    urls = [u for u in urls if u.startswith(site_url + "/") or u == site_url]
    for start in range(0, len(urls), MAX_URLS):
        batch = urls[start:start + MAX_URLS]
        payload = {
            "host": host,
            "key": key,
            "keyLocation": f"{site_url}/{key}.txt",
            "urlList": batch,
        }
        if args.dry_run:
            print(json.dumps(payload, indent=2))
            continue
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
        except urllib.error.HTTPError as err:
            # 403: key not valid (key file missing or wrong); 422: URLs
            # don't belong to the host; 429: too many requests.
            warn(f"Submission rejected: HTTP {err.code} {err.reason}.")
            return
        except urllib.error.URLError as err:
            warn(f"Couldn't reach {ENDPOINT}: {err.reason}.")
            return
        print(f"IndexNow: submitted {len(batch)} URL(s), HTTP {status}.")
        for url in batch:
            print(f"  {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="print URLs that changed since the live site")
    p.add_argument("--site", default="_site", help="built site folder")
    p.add_argument("--live", help="URL of the live sitemap.xml")
    p.add_argument("--all", action="store_true", help="list every sitemap URL")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("submit", help="post a list of URLs to IndexNow")
    p.add_argument("--urls", required=True, help="file with one URL per line")
    p.add_argument("--site-url", required=True,
                   help="site URL including any base path, e.g. https://example.com")
    p.add_argument("--key-dir", default=str(ROOT), help="folder holding <key>.txt")
    p.add_argument("--dry-run", action="store_true", help="print, don't send")
    p.set_defaults(func=cmd_submit)

    args = parser.parse_args()
    if args.command == "list" and not (args.all or args.live):
        parser.error("list needs --live or --all")
    args.func(args)


if __name__ == "__main__":
    main()
