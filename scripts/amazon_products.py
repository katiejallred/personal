#!/usr/bin/env python3
"""Fetch Amazon product images for posts that set `product_images: true`.

Amazon Associates only allows product images that come from the Product
Advertising API and are served from Amazon's own image servers, so this
script asks PA-API 5 (GetItems) for every ASIN linked from those posts and
writes what it gets to _data/amazon_products.json. The Jekyll plugin
_plugins/amazon_product_images.rb then shows a linked thumbnail in front of
each table cell or list item that starts with one of those links.

Run it before `jekyll build`:

    AMAZON_PAAPI_ACCESS_KEY=… AMAZON_PAAPI_SECRET_KEY=… python3 scripts/amazon_products.py

Standard library only. It never fails the build: without keys, or when the
API returns an error, it prints why and writes an empty file, and the posts
simply render without thumbnails. The keys are never printed.
"""

import datetime as dt
import hashlib
import hmac
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

HOST = "webservices.amazon.com"
REGION = "us-east-1"
SERVICE = "ProductAdvertisingAPI"
PATH = "/paapi5/getitems"
TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems"
MARKETPLACE = "www.amazon.com"
RESOURCES = [
    "Images.Primary.Small",
    "Images.Primary.Medium",
    "Images.Primary.Large",
    "ItemInfo.Title",
]
BATCH = 10  # GetItems accepts at most ten ItemIds per request
PAUSE = 1.1  # seconds between requests; PA-API allows about one per second

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


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def signed_request(access_key, secret_key, payload):
    """Build a SigV4-signed urllib request for PA-API 5."""
    now = dt.datetime.now(dt.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    headers = {
        "content-encoding": "amz-1.0",
        "content-type": "application/json; charset=utf-8",
        "host": HOST,
        "x-amz-date": amz_date,
        "x-amz-target": TARGET,
    }
    signed_headers = ";".join(sorted(headers))
    canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted(headers))
    canonical_request = "\n".join(
        ["POST", PATH, "", canonical_headers, signed_headers, hashlib.sha256(body).hexdigest()]
    )
    scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign = "\n".join(
        ["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical_request.encode()).hexdigest()]
    )
    k_date = sign(("AWS4" + secret_key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, REGION)
    k_service = sign(k_region, SERVICE)
    k_signing = sign(k_service, "aws4_request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    request = urllib.request.Request(f"https://{HOST}{PATH}", data=body, method="POST")
    for k, v in headers.items():
        if k != "host":
            request.add_header(k, v)
    request.add_header(
        "Authorization",
        f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}",
    )
    return request


class ApiError(Exception):
    pass


def describe_error(status, body):
    """'HTTP 401 UnrecognizedClient: The Access Key ID … is invalid.'"""
    try:
        data = json.loads(body)
    except ValueError:
        data = {}
    errors = data.get("Errors") or []
    if errors:
        detail = "; ".join(f"{e.get('Code', '?')}: {e.get('Message', '')}" for e in errors)
    elif data.get("__type"):
        detail = str(data["__type"])
    else:
        detail = body.strip()[:300] or "(empty response)"
    return f"HTTP {status} {detail}"


def get_items(access_key, secret_key, tag, asins):
    payload = {
        "ItemIds": asins,
        "ItemIdType": "ASIN",
        "PartnerTag": tag,
        "PartnerType": "Associates",
        "Marketplace": MARKETPLACE,
        "Resources": RESOURCES,
    }
    for attempt in range(3):
        request = signed_request(access_key, secret_key, payload)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8", "replace")
            if err.code == 429 and attempt < 2:
                log(f"rate limited (HTTP 429); retrying in {2 ** (attempt + 1)}s")
                time.sleep(2 ** (attempt + 1))
                continue
            raise ApiError(describe_error(err.code, body)) from None
        except urllib.error.URLError as err:
            raise ApiError(f"could not reach {HOST}: {err.reason}") from None
    raise ApiError("rate limited (HTTP 429) three times in a row")


def image(entry):
    if not entry or not entry.get("URL"):
        return None
    return {"url": entry["URL"], "width": entry.get("Width"), "height": entry.get("Height")}


def collect(result, products):
    """Add each returned item to `products`; report the ones Amazon rejected."""
    for item in result.get("ItemsResult", {}).get("Items", []):
        asin = item.get("ASIN")
        primary = item.get("Images", {}).get("Primary", {})
        images = {
            size: image(primary.get(size.capitalize()))
            for size in ("small", "medium", "large")
        }
        images = {k: v for k, v in images.items() if v}
        if not asin or not images:
            continue
        title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue")
        products[asin] = {"title": title, "url": item.get("DetailPageURL"), "images": images}
    for err in result.get("Errors", []):
        log(f"  skipped: {err.get('Code', '?')}: {err.get('Message', '')}")


def write(products):
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, sort_keys=True)
        f.write("\n")


def main():
    access_key = os.environ.get("AMAZON_PAAPI_ACCESS_KEY", "").strip()
    secret_key = os.environ.get("AMAZON_PAAPI_SECRET_KEY", "").strip()
    products = {}

    flagged, asins = find_asins()
    log(f"{flagged} post(s) with product_images: true, {len(asins)} ASIN(s) linked")

    if not asins:
        write(products)
        return
    if not access_key or not secret_key:
        log("AMAZON_PAAPI_ACCESS_KEY / AMAZON_PAAPI_SECRET_KEY not set; writing an empty file")
        write(products)
        return
    tag = partner_tag()
    if not tag:
        log("no partner tag (amazon.tag in _config.yml); writing an empty file")
        write(products)
        return

    failed = None
    for start in range(0, len(asins), BATCH):
        batch = asins[start : start + BATCH]
        if start:
            time.sleep(PAUSE)
        try:
            collect(get_items(access_key, secret_key, tag, batch), products)
        except ApiError as err:
            failed = str(err)
            log(f"API error: {failed}")
            break
        log(f"  batch {start // BATCH + 1}: {len(batch)} requested, {len(products)} image(s) so far")

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
