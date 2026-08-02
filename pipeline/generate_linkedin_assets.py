"""Generate configured Elixpo LinkedIn assets from individual Markdown files."""

import argparse
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = REPO_ROOT / "prompts" / "social" / "linkedin" / "prompts"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pipeline.generate_assets import download_to  # noqa: E402
from pipeline.linkedin_compose import compose_asset  # noqa: E402


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


def read_config(path):
    config = {}
    for line in read_section(path, "Config").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            config[key.strip().lower()] = value.strip()
    return config


def discover():
    return {
        path.stem: path
        for path in sorted(PROMPT_DIR.glob("*.md"))
        if path.stem.lower() != "readme"
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Elixpo LinkedIn assets.")
    parser.add_argument("assets", nargs="*", help="Asset IDs; omit to generate all.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    assets = discover()
    if args.list:
        for asset_id, path in assets.items():
            config = read_config(path)
            print("%-12s %sx%s  %s  → %s" % (
                asset_id,
                config.get("width", "?"),
                config.get("height", "?"),
                config.get("model", "flux"),
                config.get("output", "?"),
            ))
        return 0

    selected = args.assets or list(assets)
    unknown = [asset_id for asset_id in selected if asset_id not in assets]
    if unknown:
        for asset_id in unknown:
            print("Unknown LinkedIn asset: %s" % asset_id, file=sys.stderr)
        return 2

    generated = 0
    for asset_id in selected:
        path = assets[asset_id]
        config = read_config(path)
        prompt = read_section(path, "Prompt").replace("\n", " ")
        try:
            width = int(config["width"])
            height = int(config["height"])
            output = (REPO_ROOT / config["output"]).resolve()
        except (KeyError, ValueError) as exc:
            print("Invalid config for %s: %s" % (asset_id, exc), file=sys.stderr)
            continue
        model = config.get("model", "flux")

        if output.exists() and not args.force:
            print("[locked] %s — use --force to reroll" % asset_id)
            final_output = compose_asset(path)
            if final_output:
                print("  composited -> %s" % final_output)
            continue
        if not prompt:
            print("[skip] %s — missing ## Prompt" % asset_id)
            continue

        ok = download_to(prompt, output, width=width, height=height,
                         seed=args.seed, model=model)
        if ok:
            final_output = compose_asset(path)
            if final_output:
                print("  composited -> %s" % final_output)
            generated += 1
            time.sleep(8)

    print("Done. Generated %d LinkedIn asset(s)." % generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
