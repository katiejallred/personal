#!/usr/bin/env python3
"""Render 1200x630 Open Graph share cards in the Katie Allred design system.

Called by _plugins/og_images.rb during the Jekyll build. Reads a JSON list of
jobs on stdin, each {"title", "kicker", "out"}, and writes one PNG per job:
the red hero ground and WaveBand, the KA wordmark, an optional Caveat kicker
(a post's category), the title in Bricolage Grotesque, and Katie's headshot.

Needs Pillow (pip install pillow); it reads the site's own woff2 fonts.
Run by hand to preview:  echo '[{"title":"Hello","kicker":"Life",
"out":"/tmp/og.png"}]' | python3 scripts/og_image.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
HEADSHOT = ROOT / "assets" / "images" / "katie-allred.jpg"

W, H = 1200, 630
SCALE = 2  # draw at 2x, then downsample, for smooth curves and text

# Design system tokens (assets/css/main.css).
RED = "#D92B20"
WAVE_BACK = "#E4402F"
POPPY = (0xFF, 0x5B, 0x3A, 191)  # opacity .75
BUTTER = "#F7C548"
WHITE = "#FFFFFF"
SHELL = "#FFF3EE"
ON_RED_SOFT = "#FFE7E0"

PAD = 72
PHOTO = 300
TEXT_W = W - PAD * 3 - PHOTO


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / f"{name}-latin.woff2"), size * SCALE)
    if weight is not None:
        axes = {a["name"]: a for a in f.get_variation_axes()}
        f.set_variation_by_axes(
            [weight if n == b"Weight" else a["default"] for n, a in axes.items()]
        )
    return f


def wrap(draw, text, fnt, width):
    """Break on plain spaces only, so a non-breaking space keeps words together."""
    lines, line = [], ""
    for word in text.split(" "):
        if not word:
            continue
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=fnt) > width * SCALE:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def fit_title(draw, title, max_lines):
    """Largest Bricolage size that fits the title in max_lines lines."""
    for size in (76, 70, 64, 58, 52, 46):
        fnt = font("bricolage-grotesque", size)
        lines = wrap(draw, title, fnt, TEXT_W)
        if len(lines) <= max_lines:
            return fnt, size, lines
    lines = lines[:max_lines]
    while draw.textlength(lines[-1] + "…", font=fnt) > TEXT_W * SCALE:
        lines[-1] = lines[-1].rsplit(" ", 1)[0]
    lines[-1] = lines[-1].rstrip(",:;–—-") + "…"
    return fnt, size, lines


def cubic(p0, p1, p2, p3, steps=48):
    return [
        (
            (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t**3 * p3[0],
            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t**3 * p3[1],
        )
        for t in (i / steps for i in range(steps + 1))
    ]


def wave(start, c1, c2, mid, c3, end, top, height):
    """The WaveBand SVG paths (viewBox 1440x600), mapped onto the card.

    The second segment of each path is an SVG "S" curve, whose first control
    point mirrors c2 through mid.
    """
    c_reflect = (2 * mid[0] - c2[0], 2 * mid[1] - c2[1])
    pts = cubic(start, c1, c2, mid) + cubic(mid, c_reflect, c3, end)[1:]
    pts += [(1440, 600), (0, 600)]
    sx, sy = W * SCALE / 1440, height * SCALE / 600
    return [(x * sx, top * SCALE + y * sy) for x, y in pts]


def tile_mask(size):
    """The wordmark tile's shape: 13px corners, 4px bottom-left (scaled)."""
    big, small = (Image.new("L", (size, size), 0) for _ in range(2))
    box = (0, 0, size - 1, size - 1)
    ImageDraw.Draw(big).rounded_rectangle(box, radius=size * 13 // 34, fill=255, corners=(True, True, True, False))
    ImageDraw.Draw(small).rounded_rectangle(box, radius=size * 4 // 34, fill=255)
    return ImageChops.multiply(big, small)


def headshot():
    size = PHOTO * SCALE
    ring = 10 * SCALE
    photo = ImageOps.fit(Image.open(HEADSHOT).convert("RGB"), (size - 2 * ring,) * 2)
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *photo.size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, size, size), fill=SHELL)
    out.paste(photo, (ring, ring), mask)
    return out


def render(title, kicker, out, photo):
    img = Image.new("RGBA", (W * SCALE, H * SCALE), RED)
    draw = ImageDraw.Draw(img)

    # WaveBand, as on the hero sections.
    band_top, band_h = H - 190, 190
    draw.polygon(wave((0, 420), (300, 200), (560, 520), (880, 300), (1300, 160), (1440, 260), band_top, band_h), fill=WAVE_BACK)
    front = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(front).polygon(wave((0, 520), (360, 400), (700, 600), (1040, 470), (1360, 420), (1440, 470), band_top, band_h), fill=POPPY)
    img.alpha_composite(front)

    # Wordmark: the KA tile (white on red, flipped for the red ground) + name.
    s = SCALE
    tile = 52
    img.paste(WHITE, (PAD * s, PAD * s), tile_mask(tile * s))
    mark = font("bricolage-grotesque", 24)
    draw.text(((PAD + tile / 2) * s, (PAD + tile / 2) * s), "KA", font=mark, fill=RED, anchor="mm")
    name = font("bricolage-grotesque", 34)
    draw.text(((PAD + tile + 16) * s, (PAD + tile / 2) * s), "Katie Allred", font=name, fill=WHITE, anchor="lm")

    # Kicker + title, vertically centred in the space between wordmark and wave.
    area_top, area_bottom = PAD + tile + 36, H - 150
    kick_font = font("caveat", 52)
    kick_h = 64 if kicker else 0
    fnt, size, lines = fit_title(draw, title, 4 if not kicker else 3)
    line_h = round(size * 1.04)
    block = kick_h + line_h * len(lines)
    y = area_top + max(0, (area_bottom - area_top - block) / 2)
    if kicker:
        draw.text((PAD * s, y * s), kicker, font=kick_font, fill=BUTTER)
        y += kick_h
    for line in lines:
        draw.text((PAD * s, y * s), line, font=fnt, fill=WHITE)
        y += line_h

    # Headshot, right side, overlapping the wave.
    img.alpha_composite(photo, ((W - PAD - PHOTO) * s, ((H - PHOTO) // 2 - 10) * s))

    # Site address on the wave.
    domain = font("dm-sans", 26, weight=700)
    draw.text((PAD * s, (H - 44) * s), "katieallred.com", font=domain, fill=ON_RED_SOFT, anchor="ls")

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(out, "PNG", optimize=True)


def main():
    jobs = json.load(sys.stdin)
    photo = headshot()
    for job in jobs:
        render(job["title"], job.get("kicker") or "", job["out"], photo)


if __name__ == "__main__":
    main()
