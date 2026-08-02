"""Generate an Elixpo Blogs outreach card from an existing Oreo sticker.

This is a fully local Pillow workflow: it does not call an image model or use
generation credits.

Example:
    python3 pipeline/generate_outreach_card.py \
      --sticker 053_reading_book \
      --headline "That idea deserves a URL" \
      --description "Give it a beautiful place to live, then send it anywhere." \
      --out branding/og/blogs.elixpo/outreach/write.png
"""

import argparse
import sys
from pathlib import Path

try:
    from pipeline.outreach_compose import compose_sticker_card
except ImportError:
    # Support direct execution from the repository root.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from outreach_compose import compose_sticker_card


REPO_ROOT = Path(__file__).resolve().parent.parent
STICKER_DIR = REPO_ROOT / "stickers"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "branding" / "og" / "blogs.elixpo" / "outreach"


def resolve_sticker(value):
    """Resolve a sticker stem, filename, or explicit PNG path."""
    requested = Path(value)

    if requested.parent != Path("."):
        candidate = requested.expanduser().resolve()
    else:
        filename = requested.name
        if not filename.lower().endswith(".png"):
            filename += ".png"
        candidate = STICKER_DIR / filename

    if not candidate.is_file():
        raise FileNotFoundError("sticker not found: %s" % candidate)
    if candidate.suffix.lower() != ".png":
        raise ValueError("sticker must be a PNG: %s" % candidate)
    return candidate


def default_output(sticker_path):
    return DEFAULT_OUTPUT_DIR / (sticker_path.stem + "-card.png")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compose a 1280x720 outreach card from an Oreo sticker using Pillow.",
    )
    parser.add_argument(
        "--sticker",
        required=True,
        help="Sticker stem, filename, or PNG path (for example 053_reading_book).",
    )
    parser.add_argument("--headline", required=True, help="Large serif headline.")
    parser.add_argument(
        "--description",
        required=True,
        help="Supporting copy; wraps automatically and may contain newlines.",
    )
    parser.add_argument(
        "--eyebrow",
        default="A NOTE FROM OREO",
        help='Small tracked label (default: "A NOTE FROM OREO").',
    )
    parser.add_argument(
        "--url",
        default="blogs.elixpo.com",
        help='Bottom-left URL (default: "blogs.elixpo.com").',
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output PNG path; defaults to branding/og/blogs.elixpo/outreach/<sticker>-card.png.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        sticker = resolve_sticker(args.sticker)
    except (FileNotFoundError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    output = Path(args.out).expanduser() if args.out else default_output(sticker)
    if not output.is_absolute():
        output = REPO_ROOT / output

    compose_sticker_card(
        sticker_path=sticker,
        out_path=output,
        eyebrow=args.eyebrow,
        headline=args.headline,
        description=args.description,
        url=args.url,
    )
    print("Outreach card saved → %s" % output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
