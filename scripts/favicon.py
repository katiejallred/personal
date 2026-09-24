#!/usr/bin/env python3
"""Draw the site icons from the design system's wordmark tile: "KA" in white
Bricolage Grotesque on the red tile, 13/34 corners with a 4/34 bottom-left.

Writes favicon.svg (glyphs as outlines, so it needs no web font),
favicon.ico (16/32/48), apple-touch-icon.png (180) and icon-192/512.png to
the site root. The outputs are committed; rerun only to change the design:

    pip install pillow fonttools brotli
    python3 scripts/favicon.py
"""
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "bricolage-grotesque-latin.woff2"

RED = "#D92B20"
WHITE = "#FFFFFF"
S = 512  # SVG viewBox size
R_BIG, R_SMALL = S * 13 / 34, S * 4 / 34
TEXT = "KA"
TEXT_W = 0.68  # share of the tile width the letters take
TRACK = -0.06  # letter-spacing in em, as in .wordmark-tile


def tile_path():
    b, s = round(R_BIG, 1), round(R_SMALL, 1)
    return (
        f"M{b} 0H{S - b}A{b} {b} 0 0 1 {S} {b}V{S - b}A{b} {b} 0 0 1 {S - b} {S}"
        f"H{s}A{s} {s} 0 0 1 0 {S - s}V{b}A{b} {b} 0 0 1 {b} 0Z"
    )


def letters_path():
    font = TTFont(str(FONT))
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": 800, "opsz": 96})
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm

    # Lay the glyphs out in font units, then scale and centre them.
    x, layout = 0, []
    for ch in TEXT:
        name = cmap[ord(ch)]
        layout.append((name, x))
        x += glyphs[name].width + TRACK * upem
    bounds = BoundsPen(glyphs)
    for name, dx in layout:
        glyphs[name].draw(TransformPen(bounds, (1, 0, 0, 1, dx, 0)))
    x0, y0, x1, y1 = bounds.bounds
    scale = S * TEXT_W / (x1 - x0)
    ox = (S - (x1 - x0) * scale) / 2 - x0 * scale
    oy = (S + (y1 - y0) * scale) / 2 + y0 * scale  # flip y: font is y-up

    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for name, dx in layout:
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, ox + dx * scale, oy)))
    return pen.getCommands()


def main():
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}">'
        f'<path fill="{RED}" d="{tile_path()}"/>'
        f'<path fill="{WHITE}" d="{letters_path()}"/></svg>\n'
    )
    (ROOT / "favicon.svg").write_text(svg)

    # Raster sizes: the same tile and letters drawn with Pillow at 8x, then
    # downsampled (Pillow cannot read the SVG).

    def render(size, pad=0.0, bg=None):
        big = size * 8
        inner = round(big * (1 - 2 * pad))
        img = Image.new("RGBA", (big, big), bg or (0, 0, 0, 0))
        m1, m2 = (Image.new("L", (inner, inner), 0) for _ in range(2))
        box = (0, 0, inner - 1, inner - 1)
        ImageDraw.Draw(m1).rounded_rectangle(box, radius=inner * 13 // 34, fill=255, corners=(True, True, True, False))
        ImageDraw.Draw(m2).rounded_rectangle(box, radius=inner * 4 // 34, fill=255)
        off = (big - inner) // 2
        img.paste(RED, (off, off), ImageChops.multiply(m1, m2))

        # Letters: draw large, crop to the ink, scale to TEXT_W of the tile
        # and centre, the same geometry as the SVG.
        f = ImageFont.truetype(str(FONT), 1000)
        layer = Image.new("L", (3000, 1600), 0)
        x = 100
        for ch in TEXT:
            ImageDraw.Draw(layer).text((x, 1200), ch, font=f, fill=255, anchor="ls")
            x += f.getlength(ch) + TRACK * f.size
        ink = layer.crop(layer.getbbox())
        w = round(inner * TEXT_W)
        ink = ink.resize((w, round(ink.height * w / ink.width)), Image.LANCZOS)
        img.paste(WHITE, ((big - ink.width) // 2, (big - ink.height) // 2), ink)
        return img.resize((size, size), Image.LANCZOS)

    ico = [render(n) for n in (16, 32, 48)]
    ico[-1].save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:-1])
    # iOS masks its own corners and ignores transparency, so fill the square.
    render(180, pad=0.0, bg=RED).convert("RGB").save(ROOT / "apple-touch-icon.png", optimize=True)
    for n in (192, 512):
        render(n).save(ROOT / "assets" / "images" / f"icon-{n}.png", optimize=True)


if __name__ == "__main__":
    main()
