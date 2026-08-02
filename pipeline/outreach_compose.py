"""Compose tangy outreach cards around a reusable Oreo line-art stash.

The expensive image-generation step creates only a transparent story
illustration and stores it under:

    branding/og/<site>/outreach/stash/<card>.art.png

This module creates the card background, dotted field, blobs and typography
locally. It can therefore be rerun freely while iterating layout or copy:

    python3 pipeline/outreach_compose.py blogs.elixpo write
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1280, 720
MARGIN = 76
TEXT_W = 555
ART_BOX = (600, 92, 1218, 650)

CANVAS = (255, 252, 247)
INK = (33, 33, 33)
SLATE = (103, 103, 122)
MUTED = (139, 139, 151)
HAIRLINE = (221, 218, 217)
CORAL = (255, 119, 89)
PEACH = (255, 222, 199)
PINK = (255, 205, 211)
YELLOW = (255, 221, 112)

_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_SYS = Path("/usr/share/fonts/truetype/dejavu")
FONT_CANDIDATES = {
    "serif": [
        _FONT_DIR / "Fraunces-Bold.ttf",
        _FONT_DIR / "PlayfairDisplay-Bold.ttf",
        _SYS / "DejaVuSerif-Bold.ttf",
    ],
    "mono": [
        _FONT_DIR / "SpaceMono-Regular.ttf",
        _SYS / "DejaVuSansMono.ttf",
    ],
    "sans": [
        _FONT_DIR / "Inter-Regular.ttf",
        _SYS / "DejaVuSans.ttf",
    ],
}


def _font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _read_text_block(md_path):
    text = Path(md_path).read_text()
    if "## Text" not in text:
        return {}
    after = text.split("## Text", 1)[1]
    values = {}
    for line in after.splitlines():
        if line.startswith("##"):
            break
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip()
    return values


def _draw_tracked(draw, pos, value, font, fill, tracking=0):
    x, y = pos
    for char in value:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking


def _wrap(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_headline(draw, text, max_width, max_lines=3):
    for size in range(76, 43, -2):
        font = _font("serif", size)
        lines = _wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines, size
    font = _font("serif", 42)
    return font, _wrap(draw, text, font, max_width), 42


def _organic_blob(draw, center, radii, fill, points=48, wobble=0.14):
    """Draw a deterministic soft-edged-looking organic polygon."""
    cx, cy = center
    rx, ry = radii
    outline = []
    for index in range(points):
        angle = (math.tau * index) / points
        wave = 1 + wobble * math.sin(3 * angle + 0.7) + (wobble / 2) * math.sin(5 * angle)
        outline.append((cx + math.cos(angle) * rx * wave,
                        cy + math.sin(angle) * ry * wave))
    draw.polygon(outline, fill=fill)


def _background():
    image = Image.new("RGB", (W, H), CANVAS)
    draw = ImageDraw.Draw(image)

    # Dotted editorial matrix, deliberately lighter than the social accents.
    for y in range(10, H, 14):
        for x in range(10, W, 14):
            draw.ellipse((x, y, x + 2, y + 2), fill=HAIRLINE)

    # Tangy, deterministic blobs. They live behind the reusable Oreo art and
    # never enter the protected copy column.
    _organic_blob(draw, (1015, 350), (226, 245), PEACH, wobble=0.11)
    _organic_blob(draw, (1162, 150), (82, 68), PINK, wobble=0.17)
    _organic_blob(draw, (1200, 586), (96, 76), YELLOW, wobble=0.13)
    _organic_blob(draw, (786, 594), (48, 38), CORAL, wobble=0.18)

    # A couple of crisp editorial marks keep the blobs from feeling childish.
    draw.ellipse((823, 116, 876, 169), outline=INK, width=3)
    draw.arc((1114, 508, 1260, 662), 188, 292, fill=INK, width=3)
    return image


def _trim_alpha(image):
    rgba = image.convert("RGBA")
    # Crop from the alpha channel specifically. Transparent flood-filled pixels
    # retain white RGB values, so RGBA.getbbox() can incorrectly see them as
    # content and leave the expensive art layer padded to its full source size.
    bbox = rgba.getchannel("A").getbbox()
    return rgba.crop(bbox) if bbox else rgba


def _place_art(card, art_path):
    art = _trim_alpha(Image.open(art_path))
    left, top, right, bottom = ART_BOX
    max_w, max_h = right - left, bottom - top
    scale = min(max_w / art.width, max_h / art.height)
    size = (max(1, int(art.width * scale)), max(1, int(art.height * scale)))
    art = art.resize(size, Image.Resampling.LANCZOS)
    x = left + (max_w - art.width) // 2
    y = top + (max_h - art.height) // 2
    card.paste(art, (x, y), art)


def compose_sticker_card(sticker_path, out_path, headline, description,
                         eyebrow="A NOTE FROM OREO", url="blogs.elixpo.com"):
    """Create one outreach card from an existing transparent sticker."""
    image = _background()
    _place_art(image, sticker_path)
    draw = ImageDraw.Draw(image)

    eyebrow_font = _font("mono", 20)
    _draw_tracked(draw, (MARGIN, 112), eyebrow.upper(), eyebrow_font, MUTED, tracking=5)

    headline_font, headline_lines, headline_size = _fit_headline(draw, headline, TEXT_W)
    y = 182
    line_height = int(headline_size * 1.08)
    for line in headline_lines:
        draw.text((MARGIN, y), line, font=headline_font, fill=INK)
        y += line_height

    underline_y = y + 11
    draw.rounded_rectangle((MARGIN, underline_y, MARGIN + 200, underline_y + 10),
                           radius=5, fill=CORAL)

    # A deliberately narrower measure makes outreach descriptions breathe over
    # two or three lines instead of colliding with the illustration.
    sub_font = _font("sans", 22)
    sub_y = underline_y + 38
    for paragraph in description.splitlines() or [""]:
        lines = _wrap(draw, paragraph, sub_font, 505) if paragraph else [""]
        for line in lines:
            draw.text((MARGIN, sub_y), line, font=sub_font, fill=SLATE)
            sub_y += 32

    if url:
        url_font = _font("mono", 18)
        _draw_tracked(draw, (MARGIN, H - 82), url, url_font, MUTED, tracking=2)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, format="PNG", optimize=True)
    return out_path


def compose_outreach_card(card_md, art_path, out_path):
    """Backward-compatible prompt-file compositor."""
    txt = _read_text_block(card_md)
    return compose_sticker_card(
        art_path,
        out_path,
        headline=txt.get("headline", ""),
        description=txt.get("sub", ""),
        eyebrow=txt.get("eyebrow", "A NOTE FROM OREO"),
        url=txt.get("url", "blogs.elixpo.com"),
    )


def main(argv):
    site = argv[0] if argv else "blogs.elixpo"
    names = argv[1:]
    prompt_dir = Path("prompts/og") / site / "outreach" / "prompts"
    output_dir = Path("branding/og") / site / "outreach"
    prompts = sorted(prompt_dir.glob("*.md"))
    if names:
        prompts = [path for path in prompts if path.stem in names]

    count = 0
    for prompt in prompts:
        art = output_dir / "stash" / (prompt.stem + ".art.png")
        if not art.exists():
            print("  skip %s — no stashed art at %s" % (prompt.stem, art))
            continue
        out = compose_outreach_card(prompt, art, output_dir / (prompt.stem + ".png"))
        print("  composited → %s" % out)
        count += 1
    print("Done. Composited %d outreach card(s)." % count)


if __name__ == "__main__":
    main(sys.argv[1:])
