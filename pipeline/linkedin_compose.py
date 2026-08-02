"""Composite exact typography onto generated Elixpo LinkedIn artwork.

The image model creates the text-free ``*.bg.png`` design. Pillow then draws
the copy declared in the asset Markdown and writes the configured final PNG.

Usage:
    python3 pipeline/linkedin_compose.py banner
    python3 pipeline/linkedin_compose.py          # compose every configured asset
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = REPO_ROOT / "prompts" / "social" / "linkedin" / "prompts"
INK = (33, 33, 33)
SLATE = (117, 117, 138)
CORAL = (255, 119, 89)
FONT_DIR = Path(__file__).resolve().parent / "fonts"
SYS_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def read_section(path, heading):
    text = Path(path).read_text()
    marker = "## " + heading
    if marker not in text:
        return ""
    after = text.split(marker, 1)[1]
    lines = []
    for line in after.splitlines():
        if line.startswith("## "):
            break
        if line.strip():
            lines.append(line.strip())
    return "\n".join(lines)


def read_pairs(path, heading):
    values = {}
    for line in read_section(path, heading).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip()
    return values


def font(kind, size):
    candidates = {
        "serif": [
            FONT_DIR / "Fraunces-Bold.ttf",
            FONT_DIR / "PlayfairDisplay-Bold.ttf",
            SYS_FONT_DIR / "DejaVuSerif-Bold.ttf",
        ],
        "mono": [
            FONT_DIR / "SpaceMono-Regular.ttf",
            SYS_FONT_DIR / "DejaVuSansMono.ttf",
        ],
        "sans": [
            FONT_DIR / "Inter-Medium.ttf",
            Path("/usr/share/fonts/opentype/inter/Inter-Medium.otf"),
            SYS_FONT_DIR / "DejaVuSans.ttf",
        ],
        "icon": [
            Path("/usr/share/fonts/opentype/font-awesome/FontAwesome.otf"),
            Path("/usr/share/fonts/truetype/font-awesome/fontawesome-webfont.ttf"),
        ],
    }
    for path in candidates[kind]:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def dotted_background(size):
    """Return the exact warm-white dotted LinkedIn background."""
    width, height = size
    canvas = Image.new("RGB", size, (255, 252, 247))
    dots = ImageDraw.Draw(canvas)
    for y in range(8, height, 18):
        for x in range(8, width, 18):
            dots.ellipse((x, y, x + 2, y + 2), fill=(217, 217, 221))
    return canvas


def constrain_artwork(image, size, inset_value):
    """Place generated artwork inside an exact dotted canvas safe area."""
    width, height = size
    try:
        left, top, right, bottom = [
            int(value.strip()) for value in inset_value.split(",")
        ]
    except (AttributeError, ValueError):
        raise ValueError("art_inset must be left,top,right,bottom")
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("art_inset lies outside the configured canvas")

    canvas = dotted_background(size)

    box_size = (right - left, bottom - top)
    artwork = ImageOps.fit(
        image.convert("RGB"), box_size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    canvas.paste(artwork, (left, top))
    return canvas


def compose_asset(md_path):
    config = read_pairs(md_path, "Config")
    text = read_pairs(md_path, "Text")
    if not config.get("final_output") or not text:
        return None

    bg_path = REPO_ROOT / config["output"]
    out_path = REPO_ROOT / config["final_output"]
    width = int(config["width"])
    height = int(config["height"])
    if not bg_path.exists():
        raise FileNotFoundError("missing generated background: %s" % bg_path)

    image = Image.open(bg_path).convert("RGB")
    if image.size != (width, height):
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    if config.get("art_inset"):
        image = constrain_artwork(image, (width, height), config["art_inset"])

    background_output = config.get("background_output")
    if background_output:
        background_path = REPO_ROOT / background_output
        background_path.parent.mkdir(parents=True, exist_ok=True)
        dotted_background((width, height)).save(
            background_path, format="PNG", optimize=True, compress_level=9
        )
    draw = ImageDraw.Draw(image)

    margin = 88
    tagline = text.get("tagline", "")
    email = text.get("email", "")
    github = text.get("github", "")
    tagline_font = font("serif", 62)
    contact_font = font("sans", 20)
    icon_font = font("icon", 22)

    # Vertically centered within LinkedIn's safe left-hand copy region.
    tagline_y = 96
    if tagline:
        draw.text((margin, tagline_y), tagline, font=tagline_font, fill=INK)
        tagline_box = draw.textbbox((margin, tagline_y), tagline, font=tagline_font)
        rule_y = tagline_box[3] + 15
        draw.rounded_rectangle(
            (margin, rule_y, margin + 230, rule_y + 7), radius=4, fill=CORAL
        )
    else:
        rule_y = tagline_y

    contact_x = margin + 38
    email_y = rule_y + 24
    github_y = email_y + 39
    if email:
        # Font Awesome envelope: stable vector glyph rendered by Pillow.
        draw.text((margin, email_y - 1), "\uf0e0", font=icon_font, fill=CORAL)
        draw.text((contact_x, email_y), email, font=contact_font, fill=SLATE)
    if github:
        # Official GitHub mark from the locally installed Font Awesome font.
        draw.text((margin, github_y - 2), "\uf09b", font=icon_font, fill=INK)
        draw.text((contact_x, github_y), github, font=contact_font, fill=INK)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, format="PNG", optimize=True, compress_level=9)
    return out_path


def main(args):
    selected = set(args)
    count = 0
    for md_path in sorted(PROMPT_DIR.glob("*.md")):
        if selected and md_path.stem not in selected:
            continue
        try:
            output = compose_asset(md_path)
        except (FileNotFoundError, ValueError) as exc:
            print("[skip] %s: %s" % (md_path.stem, exc))
            continue
        if output:
            print("composited -> %s" % output)
            count += 1
    print("Done. Composited %d LinkedIn asset(s)." % count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
