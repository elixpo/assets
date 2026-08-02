"""Generate LixBlogs creator-badge prototypes from individual Markdown prompts.

The script discovers every ``prompts/*.md`` file, prepends ``STYLE.md``, calls
the repository's existing Pollinations downloader with ``model=klein``, and
corner-flood-fills the pure-white background to transparency.
"""

import argparse
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_ROOT = REPO_ROOT / "prompts" / "icons" / "blogs.elixpo" / "blogs_badges"
PROMPT_DIR = PROMPT_ROOT / "prompts"
STYLE_PATH = PROMPT_ROOT / "STYLE.md"
OUTPUT_DIR = REPO_ROOT / "branding" / "icons" / "blogs.elixpo" / "blogs_badges"
MODEL = "flux"
SIZE = 1024

# Make imports work both as ``python -m pipeline...`` and as a direct script.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.generate_assets import download_to  # noqa: E402
from pipeline.sticker_transparency import make_transparent  # noqa: E402


def read_prompt_block(path):
    """Return the text following ``## Prompt`` up to the next H2 heading."""
    text = Path(path).read_text()
    marker = "## Prompt"
    if marker not in text:
        return ""
    after = text.split(marker, 1)[1]
    lines = []
    for line in after.splitlines():
        if line.startswith("## "):
            break
        if line.strip():
            lines.append(line.strip().lstrip(">").strip())
    return " ".join(lines)


def discover_prompts():
    return {
        path.stem: path
        for path in sorted(PROMPT_DIR.glob("*.md"))
        if path.stem.lower() not in {"readme", "style"}
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate LixBlogs badge PNG prototypes with Pollinations Flux.",
    )
    parser.add_argument("badges", nargs="*", help="Badge IDs; omit to generate all.")
    parser.add_argument("--seed", type=int, default=42, help="Pollinations seed (default 42).")
    parser.add_argument("--force", action="store_true", help="Reroll existing locked assets.")
    parser.add_argument("--list", action="store_true", help="List discovered badge IDs and exit.")
    return parser.parse_args()


def main():
    args = parse_args()
    prompts = discover_prompts()
    if not prompts:
        print("No badge prompts found in %s" % PROMPT_DIR, file=sys.stderr)
        return 1

    if args.list:
        for badge_id in prompts:
            print(badge_id)
        return 0

    selected = args.badges or list(prompts)
    unknown = [badge_id for badge_id in selected if badge_id not in prompts]
    if unknown:
        for badge_id in unknown:
            print("Unknown badge: %s" % badge_id, file=sys.stderr)
        return 2

    shared = read_prompt_block(STYLE_PATH)
    if not shared:
        print("Missing ## Prompt block in %s" % STYLE_PATH, file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0
    print("Generating %d LixBlogs badge(s) [model=%s, seed=%d]" %
          (len(selected), MODEL, args.seed))

    for badge_id in selected:
        output = OUTPUT_DIR / (badge_id + ".png")
        if output.exists() and not args.force:
            print("  [locked] %s — use --force to reroll" % badge_id)
            continue

        individual = read_prompt_block(prompts[badge_id])
        if not individual:
            print("  [skip] %s — missing ## Prompt block" % badge_id)
            continue

        full_prompt = "%s Badge-specific direction: %s" % (shared, individual)
        ok = download_to(full_prompt, output, width=SIZE, height=SIZE,
                         seed=args.seed, model=MODEL)
        if not ok:
            continue

        try:
            make_transparent(output, output, tolerance=24)
            print("  transparent → %s" % output)
        except Exception as exc:
            print("  warning: transparency failed for %s: %s" % (badge_id, exc))
        generated += 1
        time.sleep(8)

    print("Done. Generated %d new badge(s) → %s" % (generated, OUTPUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
