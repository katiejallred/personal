#!/usr/bin/env python3
"""Draw 1080x1080 social-share cards for blog posts in the Katie Allred design system.

Each card is the post's featured photo on top, the brand WaveBand running into
the red hero ground, an optional Caveat kicker, the title in Bricolage
Grotesque, the KA wordmark and the site address. The output goes under
assets/images/social/, so a card can be attached to a social post by URL
once the site deploys.

Usage:
    python3 scripts/social_image.py _posts/2026-10-06-some-post.md [more posts…]
    python3 scripts/social_image.py --kicker "Prime Big Deal Days" _posts/…

Reads the post's `title` and `image` from its front matter (Pillow only,
same fonts as scripts/og_image.py). Prints the path of each card it writes.
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT_DIR = ROOT / "assets" / "images" / "social"

W = H = 1080
SCALE = 2
PAD = 72
PHOTO_H = 470  # the photo's height before the wave takes over

RED = "#D92B20"
WAVE_BACK = "#E4402F"
POPPY = (0xFF, 0x5B, 0x3A, 191)
BUTTER = "#F7C548"
WHITE = "#FFFFFF"
ON_RED_SOFT = "#FFE7E0"


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / f"{name}-latin.woff2"), size * SCALE)
    if weight is not None:
        axes = {a["name"]: a for a in f.get_variation_axes()}
        f.set_variation_by_axes([weight if n == b"Weight" else a["default"] for n, a in axes.items()])
    return f


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split(" "):
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=fnt) > width * SCALE:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def fit_title(draw, title, width, height, max_lines):
    """Largest Bricolage size whose wrapped lines fit the width and height."""
    for size in (80, 74, 68, 62, 56, 50, 46):
        fnt = font("bricolage-grotesque", size)
        lines = wrap(draw, title, fnt, width)
        if len(lines) <= max_lines and len(lines) * round(size * 1.04) <= height:
            return fnt, size, lines
    return fnt, size, lines[:max_lines]


def cubic(p0, p1, p2, p3, steps=48):
    return [
        (
            (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t**3 * p3[0],
            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t**3 * p3[1],
        )
        for t in (i / steps for i in range(steps + 1))
    ]


def wave(start, c1, c2, mid, c3, end, top, height):
    """A WaveBand path (viewBox 1440x600) mapped onto the card, filled below the curve."""
    c_reflect = (2 * mid[0] - c2[0], 2 * mid[1] - c2[1])
    pts = cubic(start, c1, c2, mid) + cubic(mid, c_reflect, c3, end)[1:]
    pts += [(1440, 600), (0, 600)]
    sx, sy = W * SCALE / 1440, height * SCALE / 600
    return [(x * sx, top * SCALE + y * sy) for x, y in pts]


def tile_mask(size):
    from PIL import ImageChops
    big, small = (Image.new("L", (size, size), 0) for _ in range(2))
    box = (0, 0, size - 1, size - 1)
    ImageDraw.Draw(big).rounded_rectangle(box, radius=size * 13 // 34, fill=255, corners=(True, True, True, False))
    ImageDraw.Draw(small).rounded_rectangle(box, radius=size * 4 // 34, fill=255)
    return ImageChops.multiply(big, small)


def front_matter(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    data = {}
    for line in (m.group(1) if m else "").splitlines():
        km = re.match(r"^(\w+):\s*(.*)$", line)
        if km:
            data[km.group(1)] = km.group(2).strip().strip("'\"")
    return data


def render(title, photo_path, kicker, out):
    s = SCALE
    img = Image.new("RGBA", (W * s, H * s), RED)
    photo = ImageOps.fit(Image.open(photo_path).convert("RGB"), (W * s, (PHOTO_H + 80) * s))
    img.paste(photo, (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    # WaveBand as the seam between photo and ground: a lighter back wave,
    # a translucent poppy wave, then the red ground.
    band_top, band_h = PHOTO_H - 60, 170
    draw.polygon(wave((0, 420), (300, 200), (560, 520), (880, 300), (1300, 160), (1440, 260), band_top, band_h), fill=WAVE_BACK)
    draw.polygon(wave((0, 520), (360, 400), (700, 600), (1040, 470), (1360, 420), (1440, 470), band_top + 30, band_h), fill=POPPY)
    draw.polygon(wave((0, 560), (360, 470), (700, 600), (1040, 520), (1360, 500), (1440, 540), band_top + 60, band_h), fill=RED)

    # Kicker + title on the red ground, above the footer row.
    tile = 48
    footer_top = H - PAD - tile
    y = PHOTO_H + 160
    text_w = W - 2 * PAD
    if kicker:
        draw.text((PAD * s, y * s), kicker, font=font("caveat", 60), fill=BUTTER)
        y += 76
    fnt, size, lines = fit_title(draw, title, text_w, footer_top - 28 - y, 4)
    line_h = round(size * 1.04)
    for line in lines:
        draw.text((PAD * s, y * s), line, font=fnt, fill=WHITE)
        y += line_h

    # Wordmark bottom-left, site address bottom-right.
    ty = footer_top
    img.paste(WHITE, (PAD * s, ty * s), tile_mask(tile * s))
    draw.text(((PAD + tile / 2) * s, (ty + tile / 2) * s), "KA", font=font("bricolage-grotesque", 22), fill=RED, anchor="mm")
    draw.text(((PAD + tile + 14) * s, (ty + tile / 2) * s), "Katie Allred", font=font("bricolage-grotesque", 30), fill=WHITE, anchor="lm")
    draw.text(((W - PAD) * s, (ty + tile / 2) * s), "katieallred.com", font=font("dm-sans", 26, weight=700), fill=ON_RED_SOFT, anchor="rm")

    out.parent.mkdir(parents=True, exist_ok=True)
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--kicker", default="")
    args = ap.parse_args()
    for post in args.posts:
        fm = front_matter(post)
        title, image = fm.get("title"), fm.get("image")
        if not title or not image:
            print(f"{post}: needs title and image in front matter", file=sys.stderr)
            continue
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", Path(post).stem)
        out = render(title, ROOT / image.lstrip("/"), args.kicker, OUT_DIR / f"{slug}.jpg")
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
