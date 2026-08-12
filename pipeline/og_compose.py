"""Composite OG card text onto an AI-generated design.

The AI generates the DESIGN ONLY (text-free: dotted matrix, entangled one-line
Oreo, a couple of geometric shapes) at 16:9. This script overlays the typography
ourselves with Pillow — so the model never fumbles letters — at fixed, correct
proportions in the card's left negative space.

  prompts/og/<site>/prompts/<name>.md     (## Text block: eyebrow/headline/sub/url)
  branding/og/<site>/<name>.bg.png  (AI design)
        → branding/og/<site>/<name>.png   (final card)

Usage:
  python pipeline/og_compose.py                      # every site, every card
  python pipeline/og_compose.py mails.elixpo         # one site
  python pipeline/og_compose.py mails.elixpo default # one card
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Canvas (16:9) ─────────────────────────────────────────────────────────────
W, H = 1280, 720
MARGIN = 84
COL_W = 660          # left text column; the design/panda lives to the right

# ── Palette (the light "oreo" system) ────────────────────────────────────────
INK    = (33, 33, 33)
SLATE  = (117, 117, 138)
MUTED  = (147, 147, 159)
CORAL  = (255, 119, 89)

# ── Fonts ─────────────────────────────────────────────────────────────────────
# Drop Fraunces / Space Mono / Inter .ttf into pipeline/fonts/ to upgrade from the
# DejaVu fallbacks. First existing path in each list wins.
_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_SYS = "/usr/share/fonts/truetype"
FONT_CANDIDATES = {
    "serif": [  # bold, high-contrast headline
        _FONT_DIR / "Fraunces-Bold.ttf",
        _FONT_DIR / "PlayfairDisplay-Bold.ttf",
        Path("%s/dejavu/DejaVuSerif-Bold.ttf" % _SYS),
    ],
    "mono": [  # eyebrow / url
        _FONT_DIR / "SpaceMono-Regular.ttf",
        Path("%s/dejavu/DejaVuSansMono.ttf" % _SYS),
    ],
    "sans": [  # body / sub copy
        _FONT_DIR / "Inter-Regular.ttf",
        Path("%s/dejavu/DejaVuSans.ttf" % _SYS),
    ],
}


def _font(kind, size):
    for p in FONT_CANDIDATES[kind]:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


# ── Text helpers ──────────────────────────────────────────────────────────────
def _read_key_block(md_path, heading):
    """Parse a Markdown H2 block containing ``key: value`` lines."""
    text = Path(md_path).read_text()
    marker = "## " + heading
    if marker not in text:
        return {}
    after = text.split(marker, 1)[1]
    out = {}
    for line in after.splitlines():
        if line.startswith("##"):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def _read_text_block(md_path):
    """Parse the `## Text` block of a card .md into a dict of key: value."""
    return _read_key_block(md_path, "Text")


def _dotted_canvas():
    """Create the deterministic Elixpo white dotted OG background."""
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(8, H, 14):
        for x in range(8, W, 14):
            draw.ellipse((x, y, x + 1, y + 1), fill=(217, 217, 221))
    return canvas


def _extract_art(img, tolerance):
    """Flood-fill a light connected background and crop opaque artwork."""
    art = img.convert("RGBA")
    w, h = art.size
    transparent = (255, 0, 255, 0)
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if art.getpixel(corner) != transparent:
            ImageDraw.floodfill(art, corner, transparent, thresh=tolerance)

    bbox = art.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("art extraction found no opaque artwork")
    return art.crop(bbox)


def _place_art(canvas, art, layout):
    """Fit extracted artwork and anchor it inside the right safe area."""
    tolerance = int(layout.get("background_tolerance", 24))
    max_width = int(layout.get("art_max_width", 390))
    max_height = int(layout.get("art_max_height", 470))
    right = int(layout.get("art_right", 40))
    top_value = layout.get("art_top", "center").strip().lower()
    art.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    x = W - right - art.width
    if top_value == "center":
        y = (H - art.height) // 2
    else:
        y = int(top_value)
    if x < COL_W + MARGIN or y < 0 or y + art.height > H:
        raise ValueError("isolated-art placement falls outside the safe canvas")

    canvas.paste(art, (x, y), art)
    return canvas


def _draw_agent_workflow(canvas):
    """Draw quiet Agent issue/branch/check scaffolding behind Oreo."""
    draw = ImageDraw.Draw(canvas)
    pale = (226, 226, 230)
    width = 2

    # Blank issue/page with a folded corner—no text-like detail.
    draw.rounded_rectangle((1112, 105, 1190, 180), radius=8,
                           outline=pale, width=width)
    draw.line((1168, 105, 1190, 127, 1168, 127, 1168, 105),
              fill=pale, width=width, joint="curve")

    # Compact three-node contribution branch.
    draw.line((1085, 278, 1135, 278, 1162, 305, 1202, 305),
              fill=pale, width=width, joint="curve")
    for cx, cy in ((1085, 278), (1162, 305), (1202, 305)):
        draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9),
                     outline=pale, width=width)

    # Completed merge/check node.
    draw.ellipse((1148, 390, 1214, 456), outline=pale, width=width)
    draw.line((1167, 423, 1183, 438, 1200, 413),
              fill=pale, width=width, joint="curve")


def _compose_isolated_art(img, layout):
    """Extract model artwork, fit it, and anchor it on a dotted canvas."""
    tolerance = int(layout.get("background_tolerance", 24))
    art = _extract_art(img, tolerance)
    canvas = _dotted_canvas()
    return _place_art(canvas, art, layout)


def _compose_asset_art(card_md, layout):
    """Reuse approved repository artwork instead of regenerating a mascot."""
    source_value = layout.get("art_source")
    if not source_value:
        raise ValueError("asset-art mode requires art_source")
    repo_root = Path(__file__).resolve().parent.parent
    source = (repo_root / source_value).resolve()
    if not source.exists():
        raise FileNotFoundError("asset-art source not found: %s" % source)

    art_img = Image.open(source).convert("RGB")
    crop_value = layout.get("art_crop")
    if crop_value:
        try:
            crop = tuple(int(value.strip()) for value in crop_value.split(","))
        except ValueError:
            raise ValueError("art_crop must be left,top,right,bottom")
        if len(crop) != 4:
            raise ValueError("art_crop must contain four integers")
        art_img = art_img.crop(crop)

    tolerance = int(layout.get("background_tolerance", 45))
    art = _extract_art(art_img, tolerance)
    canvas = _dotted_canvas()
    if layout.get("infographic", "").lower() == "agent-workflow":
        _draw_agent_workflow(canvas)
    return _place_art(canvas, art, layout)


def _text_w(draw, s, font, tracking=0):
    if not s:
        return 0
    w = sum(draw.textlength(c, font=font) for c in s)
    return int(w + tracking * (len(s) - 1))


def _draw_tracked(draw, pos, s, font, fill, tracking=0):
    """draw.text with manual letter-spacing (Pillow has none)."""
    x, y = pos
    for c in s:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + tracking
    return x


def _wrap(draw, words, font, max_w):
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_headline(draw, text, max_w, max_lines=3, hi=78, lo=40):
    """Largest serif size whose wrapped headline fits the column in ≤max_lines."""
    words = text.split()
    for size in range(hi, lo - 1, -2):
        font = _font("serif", size)
        lines = _wrap(draw, words, font, max_w)
        if len(lines) <= max_lines and all(draw.textlength(l, font=font) <= max_w for l in lines):
            return font, lines, size
    font = _font("serif", lo)
    return font, _wrap(draw, words, font, max_w), lo


# ── Compose one card ──────────────────────────────────────────────────────────
def compose_card(card_md, bg_path, out_path):
    """Overlay the card's `## Text` onto its AI design → out_path (1280×720)."""
    txt = _read_text_block(card_md)
    layout = _read_key_block(card_md, "Layout")
    eyebrow  = txt.get("eyebrow", "")
    headline = txt.get("headline", "")
    sub      = txt.get("sub", "")
    url      = txt.get("url", "")

    mode = layout.get("mode", "").lower()
    if mode == "asset-art":
        img = _compose_asset_art(card_md, layout)
    else:
        img = Image.open(bg_path).convert("RGB")
        if img.size != (W, H):
            img = img.resize((W, H), Image.LANCZOS)
        if mode == "isolated-art":
            img = _compose_isolated_art(img, layout)
    draw = ImageDraw.Draw(img)

    # Eyebrow (mono, uppercase, wide tracking)
    y = 128
    if eyebrow:
        ef = _font("mono", 22)
        _draw_tracked(draw, (MARGIN, y), eyebrow.upper(), ef, MUTED, tracking=6)
        y += 54

    # Headline (bold serif, auto-fit, wrapped)
    hf, lines, hsize = _fit_headline(draw, headline, COL_W)
    line_h = int(hsize * 1.12)
    y += 8
    head_top = y
    for ln in lines:
        draw.text((MARGIN, y), ln, font=hf, fill=INK)
        y += line_h
    head_bottom = y

    # Heavy coral underline
    ul_w = min(COL_W * 0.55, 360)
    ul_y = head_bottom + 14
    draw.rounded_rectangle([MARGIN, ul_y, MARGIN + ul_w, ul_y + 10], radius=5, fill=CORAL)

    # Sub copy (sans, slate, wrapped)
    if sub:
        sf = _font("sans", 23)
        sy = ul_y + 40
        for ln in _wrap(draw, sub.split(), sf, COL_W):
            draw.text((MARGIN, sy), ln, font=sf, fill=SLATE)
            sy += int(23 * 1.4)

    # URL (mono, bottom-left, tracked)
    if url:
        uf = _font("mono", 19)
        _draw_tracked(draw, (MARGIN, H - MARGIN - 18), url, uf, MUTED, tracking=2)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


# ── CLI: re-composite existing designs ────────────────────────────────────────
def main(argv):
    base = Path("prompts") / "og"
    if not base.exists():
        print("No %s" % base)
        return
    sites = [d for d in sorted(base.iterdir()) if d.is_dir() and not d.name.startswith(".")]

    site_filter, card_filter = None, None
    if argv:
        names = [s.name for s in sites]
        if argv[0] in names:
            site_filter, card_filter = argv[0], (argv[1:] or None)
        else:
            card_filter = argv

    n = 0
    for site in sites:
        if site_filter and site.name != site_filter:
            continue
        out_dir = Path("branding") / "og" / site.name
        for md in sorted((site / "prompts").glob("*.md")):
            if md.stem.lower() in {"readme", "style", "palette"}:
                continue
            if card_filter and md.stem not in card_filter:
                continue
            bg = out_dir / ("%s.bg.png" % md.stem)
            if not bg.exists():
                print("  skip %s/%s — no design (%s); run --og first"
                      % (site.name, md.stem, bg.name))
                continue
            out = compose_card(md, bg, out_dir / ("%s.png" % md.stem))
            print("  composited → %s" % out)
            n += 1
    print("Done. Composited %d card(s)." % n)


if __name__ == "__main__":
    main(sys.argv[1:])
