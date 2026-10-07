#!/usr/bin/env python3
"""Fetch Amazon product images for posts that set `product_images: true`.

Amazon Associates only allows product images that come from Amazon's API
and are served from Amazon's own image servers, so this script asks the
Amazon Creators API (the successor to Product Advertising API 5, same
GetItems operation) for every ASIN linked from those posts and writes what
it gets to _data/amazon_products.json. The Jekyll plugin
_plugins/amazon_product_images.rb then shows a linked thumbnail in front of
each table cell or list item that starts with one of those links.

Run it before `jekyll build` with a Creators API credential (Associates
Central → Tools → Creators API → your application):

    AMAZON_PAAPI_ACCESS_KEY=<credential ID>  AMAZON_PAAPI_SECRET_KEY=<credential secret> \
        python3 scripts/amazon_products.py

The credential is exchanged for a one-hour OAuth 2.0 bearer token at Login
with Amazon, then GetItems is called ten ASINs at a time. Credential
versions 3.1 (North America, the default), 3.2 (Europe) and 3.3 (Far East)
use different token hosts; set AMAZON_CREATORS_API_VERSION to pick one.

Standard library only. It never fails the build: without a credential, or
when Amazon returns an error, it prints why and writes an empty file, and
the posts simply render without thumbnails. The credential is never printed.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "_data", "amazon_products.json")
CONTENT_DIRS = ("_posts", "_drafts", "pages")

# Login with Amazon token hosts by Creators API credential version.
TOKEN_HOSTS = {
    "3.1": "api.amazon.com",     # North America
    "3.2": "api.amazon.co.uk",   # Europe
    "3.3": "api.amazon.co.jp",   # Far East
}
TOKEN_SCOPE = "creatorsapi::default"
API_URL = "https://creatorsapi.amazon/catalog/v1/getItems"
MARKETPLACE = "www.amazon.com"
RESOURCES = [
    "images.primary.small",
    "images.primary.medium",
    "images.primary.large",
    "itemInfo.title",
]
BATCH = 10  # GetItems accepts at most ten itemIds per request
PAUSE = 1.1  # seconds between requests; the API allows about one per second

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
FLAG = re.compile(r"^product_images:\s*true\s*$", re.M)
ASIN = re.compile(
    r"amazon\.com/(?:[^/?\"'\s)]+/)?(?:dp|gp/product)/([A-Z0-9]{10})", re.I
)


def log(*parts):
    print("Amazon product images:", *parts, flush=True)


def partner_tag():
    tag = os.environ.get("AMAZON_PARTNER_TAG")
    if tag:
        return tag
    try:
        with open(os.path.join(ROOT, "_config.yml"), encoding="utf-8") as f:
            config = f.read()
    except OSError:
        return None
    # amazon:
    #   tag: kajal04-20
    match = re.search(r"^amazon:\s*\n((?:[ \t]+.*\n?)+)", config, re.M)
    if not match:
        return None
    tag = re.search(r"^[ \t]+tag:\s*[\"']?([\w-]+)", match.group(1), re.M)
    return tag.group(1) if tag else None


def find_asins():
    """ASINs linked from every post or page flagged product_images: true."""
    asins = []
    flagged = 0
    for folder in CONTENT_DIRS:
        path = os.path.join(ROOT, folder)
        if not os.path.isdir(path):
            continue
        for name in sorted(os.listdir(path)):
            if not name.endswith((".md", ".markdown", ".html")):
                continue
            with open(os.path.join(path, name), encoding="utf-8") as f:
                text = f.read()
            front = FRONT_MATTER.match(text)
            if not front or not FLAG.search(front.group(1)):
                continue
            flagged += 1
            for asin in ASIN.findall(text):
                asin = asin.upper()
                if asin not in asins:
                    asins.append(asin)
    return flagged, asins


class ApiError(Exception):
    pass


def post_json(url, payload, headers, what):
    """POST JSON and return the parsed JSON reply; raise ApiError on failure."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        text = err.read().decode("utf-8", "replace")
        raise ApiError(f"{what}: HTTP {err.code} {describe_error(text)}") from None
    except urllib.error.URLError as err:
        raise ApiError(f"{what}: could not reach {url}: {err.reason}") from None


def describe_error(text):
    """Turn an error body into one line, whatever shape Amazon used."""
    try:
        data = json.loads(text)
    except ValueError:
        return text.strip()[:300] or "(empty response)"
    if not isinstance(data, dict):
        return text.strip()[:300]
    # Login with Amazon: {"error": "invalid_client", "error_description": "…"}
    if data.get("error"):
        return f"{data['error']}: {data.get('error_description', '')}".strip(": ")
    # Creators API: {"type": "UnauthorizedException", "reason": "InvalidToken", "message": "…"}
    if data.get("reason") or data.get("type"):
        return f"{data.get('reason') or data.get('type')}: {data.get('message', '')}".strip(": ")
    errors = data.get("errors") or data.get("Errors") or []
    if errors:
        return "; ".join(
            f"{e.get('code') or e.get('Code', '?')}: {e.get('message') or e.get('Message', '')}"
            for e in errors
        )
    return text.strip()[:300]


def access_token(client_id, client_secret):
    version = os.environ.get("AMAZON_CREATORS_API_VERSION", "3.1").strip()
    host = TOKEN_HOSTS.get(version)
    if not host:
        raise ApiError(
            f"AMAZON_CREATORS_API_VERSION={version!r} is not one of {', '.join(TOKEN_HOSTS)}"
        )
    reply = post_json(
        f"https://{host}/auth/o2/token",
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": TOKEN_SCOPE,
        },
        {},
        "token request",
    )
    token = reply.get("access_token")
    if not token:
        raise ApiError("token request: no access_token in the reply")
    return token


def get_items(token, tag, asins):
    payload = {
        "itemIds": asins,
        "itemIdType": "ASIN",
        "marketplace": MARKETPLACE,
        "partnerTag": tag,
        "resources": RESOURCES,
    }
    headers = {"Authorization": f"Bearer {token}", "x-marketplace": MARKETPLACE}
    for attempt in range(3):
        try:
            return post_json(API_URL, payload, headers, "GetItems")
        except ApiError as err:
            if "HTTP 429" in str(err) and attempt < 2:
                log(f"rate limited (HTTP 429); retrying in {2 ** (attempt + 1)}s")
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise ApiError("GetItems: rate limited (HTTP 429) three times in a row")


def image(entry):
    if not isinstance(entry, dict) or not entry.get("url"):
        return None
    return {"url": entry["url"], "width": entry.get("width"), "height": entry.get("height")}


def collect(result, products):
    """Add each returned item to `products`; report the ones Amazon rejected."""
    items = (result.get("itemsResult") or {}).get("items") or []
    for item in items:
        asin = item.get("asin")
        primary = (item.get("images") or {}).get("primary") or {}
        images = {size: image(primary.get(size)) for size in ("small", "medium", "large")}
        images = {k: v for k, v in images.items() if v}
        if not asin or not images:
            continue
        title = ((item.get("itemInfo") or {}).get("title") or {}).get("displayValue")
        products[asin] = {"title": title, "url": item.get("detailPageURL"), "images": images}
    for err in result.get("errors") or []:
        log(f"  skipped: {err.get('code', '?')}: {err.get('message', '')}")


def write(products):
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, sort_keys=True)
        f.write("\n")


def main():
    client_id = os.environ.get("AMAZON_PAAPI_ACCESS_KEY", "").strip()
    client_secret = os.environ.get("AMAZON_PAAPI_SECRET_KEY", "").strip()
    products = {}

    flagged, asins = find_asins()
    log(f"{flagged} post(s) with product_images: true, {len(asins)} ASIN(s) linked")

    if not asins:
        write(products)
        return
    if not client_id or not client_secret:
        log("AMAZON_PAAPI_ACCESS_KEY / AMAZON_PAAPI_SECRET_KEY not set; writing an empty file")
        write(products)
        return
    tag = partner_tag()
    if not tag:
        log("no partner tag (amazon.tag in _config.yml); writing an empty file")
        write(products)
        return

    failed = None
    try:
        token = access_token(client_id, client_secret)
        log("signed in to the Creators API")
        for start in range(0, len(asins), BATCH):
            batch = asins[start : start + BATCH]
            if start:
                time.sleep(PAUSE)
            collect(get_items(token, tag, batch), products)
            log(f"  batch {start // BATCH + 1}: {len(batch)} requested, {len(products)} image(s) so far")
    except ApiError as err:
        failed = str(err)
        log(f"API error: {failed}")

    write(products)
    if failed:
        log(f"fetched {len(products)} of {len(asins)} image(s) before the error above")
    else:
        log(f"fetched {len(products)} of {len(asins)} image(s) -> {os.path.relpath(OUTPUT, ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # noqa: BLE001 - never fail the build
        log(f"unexpected error: {err.__class__.__name__}: {err}")
        try:
            write({})
        except OSError:
            pass
    sys.exit(0)
