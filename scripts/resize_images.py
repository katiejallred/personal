#!/usr/bin/env python3
"""Save smaller copies of site images for responsive srcset.

Called by _plugins/responsive_images.rb during the Jekyll build. Reads a JSON
list of jobs on stdin, each {"src", "out", "width"}, and writes the image at
`src` scaled down to `width` pixels wide as `out`, in the same format:
JPEG at quality 82 (progressive), PNG optimized, WebP at quality 80. EXIF
rotation is applied, so the copies are always upright.

Needs Pillow (pip install pillow). Run by hand to test:
  echo '[{"src":"assets/images/katie-allred.jpg","out":"/tmp/k.jpg",
  "width":320}]' | python3 scripts/resize_images.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps


def resize(src, out, width):
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)
        height = round(im.height * width / im.width)
        im = im.resize((width, height), Image.LANCZOS)
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        ext = out.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.save(tmp, "JPEG", quality=82, optimize=True, progressive=True, icc_profile=icc)
        elif ext == ".png":
            im.save(tmp, "PNG", optimize=True, icc_profile=icc)
        elif ext == ".webp":
            im.save(tmp, "WEBP", quality=80, method=6, icc_profile=icc)
        else:
            raise ValueError(f"unsupported format: {src}")
        tmp.replace(out)


def main():
    failed = 0
    for job in json.load(sys.stdin):
        try:
            resize(job["src"], job["out"], int(job["width"]))
        except Exception as e:  # keep going; the plugin skips missing copies
            failed += 1
            print(f"{job['src']}: {e}", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
