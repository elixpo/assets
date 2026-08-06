"""Generate Oreo Badge assets via the Pollinations AI image API.

Top-level icons:
  python pipeline/generate_assets.py              # all active entries
  python pipeline/generate_assets.py home_bg

Per-app sprites (prompts/<app>/<name>.md → apps/<app>/assets/raw/<name>.png):
  python pipeline/generate_assets.py --app flappy           # all prompts under prompts/flappy/
  python pipeline/generate_assets.py --app flappy obstacle  # single sprite

Stickers (prompts/stickers/<name>.md → stickers/<name>.png at 1024x1024):
  python pipeline/generate_assets.py --stickers             # every sticker prompt
  python pipeline/generate_assets.py --stickers 01_hello    # single sticker
  python pipeline/generate_assets.py --stickers --seed 7    # different seed
  python pipeline/generate_assets.py --stickers --from 22   # sweep 022 → end
  python pipeline/generate_assets.py --stickers --from 22 --to 60   # range 022–060

OG cards (prompts/og/<site>/prompts/<name>.md → branding/og/<site>/<name>.png, 1280x720 16:9):
  python pipeline/generate_assets.py --og                         # every site, every card
  python pipeline/generate_assets.py --og mails.elixpo            # one site, all cards
  python pipeline/generate_assets.py --og mails.elixpo default    # one card
  python pipeline/generate_assets.py --og default docs            # those cards, every site
  python pipeline/generate_assets.py --og mails.elixpo --force    # reroll a locked card
  # finished <name>.png is LOCKED (not regenerated); .bg.png is deleted after compositing

Outreach cards (reusable art stash + locally composited social card):
  python pipeline/generate_assets.py --outreach blogs.elixpo write
  python pipeline/generate_assets.py --outreach blogs.elixpo write --force-art
  # the API-generated Oreo story is kept under outreach/stash/; rerunning
  # without --force-art only recomposes blobs, dots, copy and layout locally

Website icons (prompts/icons/<domain>/icon_prompt.md → branding/icons/web/<domain>.png):
  python pipeline/generate_assets.py --web                  # all website icons
  python pipeline/generate_assets.py --web sketch.elixpo    # single icon
  (sticker-style on a cream background, transparency applied automatically)

LixBlogs creator badge prototypes (one shared prompt file → transparent PNGs):
  python pipeline/generate_assets.py --blog-badges first-light
  python pipeline/generate_assets.py --blog-badges                    # all 25
  python pipeline/generate_assets.py --blog-badges --list             # list IDs
  python pipeline/generate_assets.py --blog-badges first-light --force
  # Uses Pollinations model=flux. Finished PNGs are locked unless --force.
  # The PNGs are vector-style approval sources; badges_prompt.md remains the
  # strict specification for the later production SVG exports.

Brand marks (prompts/brand/<variant>.md → branding/brand/<variant>.png):
  python pipeline/generate_assets.py --brand                # mascot mark, wordmark, lockup
  python pipeline/generate_assets.py --brand lockup         # single variant
  python pipeline/generate_assets.py --brand --force        # reroll a locked mark
  # Generated EXACTLY like the OG cards: the AI renders the line-art DESIGN
  #   (text-free), then Pillow composites the fancy serif headline + the
  #   "Built in the Open" sub. NO alpha-removal pass. A prompt with no `## Text`
  #   block (e.g. the panda-only mascot mark) keeps the design as the final.
  # Seed defaults to OG_SEED (the proven line-art seed); pass --seed N to explore.
  # A finished <variant>.png is LOCKED (not regenerated) — pass --force to reroll.

Mascot reference: references/MASCOT.md
"""

import os
import re
import sys
import urllib.request
import urllib.parse
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(".env.local")

KEY   = os.getenv("POLLINATIONS_KEY")
BASE  = "https://gen.pollinations.ai/image"
MODEL = "gptimage"

# Brand marks render on a wide 16:9 canvas (the logo lockup/wordmark are
# horizontal). Per-app sprites stay square (1:1). The optimiser downscales
# each to its real target size afterwards.
BRAND_W, BRAND_H = 1024, 576

# Open-graph / social cards render 16:9, full-bleed, NO cropping. The AI
# generates the DESIGN ONLY (faint dotted-matrix background, an entangled
# one-line Oreo, a couple of geometric shapes) — text-free. We composite the
# headline/eyebrow/sub/url ourselves with Pillow (pipeline/og_compose.py) so the
# model never fumbles the typography. No transparency pass.
OG_W, OG_H = 1280, 720          # 16:9
MODEL_OG   = "gptimage"         # standard GPT Image model for OG designs
MODEL_BLOG_BADGES = "flux"      # vector-style LixBlogs badge prototypes
STICKER_STYLE_SUFFIX = (
    "pixel art cartoon style, thick dark outline, vibrant warm celebration "
    "colours, cute kawaii style, sticker design with thick white border "
    "ready for die-cut, warm cream white background padded behind the main "
    "subject by about 3-5px so the subject, sparkles, confetti, motion marks "
    "and other tiny accents sit inside a solid clean backing, square crop, "
    "no text, no watermark"
)

# Locked Oreo line-art look reproduces on this seed (override only with --seed).
# Canonical reference: references/OREO-LINEART.md
OG_SEED = 7

# The brand marks are the fixed identity — they must come out IDENTICAL on
# every run. So `--brand` always pins this seed (override only by passing an
# explicit --seed). Change it and you change the official logo.
BRAND_SEED = 42


def _read_prompt(path):
    """Read prompt text from a .md file (the block after '## Prompt')."""
    md = Path(path)
    if not md.exists():
        return None
    text = md.read_text()
    marker = "## Prompt"
    if marker in text:
        after = text.split(marker, 1)[1]
        lines = []
        for line in after.splitlines():
            if line.startswith("##"):
                break
            lines.append(line)
        return " ".join(l.strip() for l in lines if l.strip())
    return None


def _normalize_sticker_prompt(prompt):
    """Force the shared sticker finish so every sticker keeps a padded solid backing."""
    old_suffix = (
        "pixel art cartoon style, thick dark outline, vibrant warm celebration "
        "colours, cute kawaii style, sticker design with thick white border "
        "ready for die-cut, warm cream white background, square crop, no text, "
        "no watermark"
    )
    if old_suffix in prompt:
        prompt = prompt.replace(old_suffix, STICKER_STYLE_SUFFIX)
    elif STICKER_STYLE_SUFFIX not in prompt:
        prompt = prompt.rstrip() + ", " + STICKER_STYLE_SUFFIX
    return prompt


def _read_blog_badge_prompts(path=None):
    """Parse the shared direction and 25 named badge prompts from one Markdown file.

    Returns a list of dictionaries with ``id``, ``title`` and a complete Flux
    prompt. Badge IDs come from the filenames in the Markdown headings, making
    the spec the single source of truth for names and ordering.
    """
    source = Path(path or
                  "prompts/icons/blogs.elixpo/blogs_badges/badges_prompt.md")
    if not source.exists():
        return []
    text = source.read_text()

    shared_start = text.find("## Shared SVG direction")
    shared_end = text.find("## Badge prompts")
    if shared_start < 0 or shared_end < 0:
        print("Invalid badge prompt document — missing shared/badge sections")
        return []
    shared = text[shared_start:shared_end]
    shared_lines = []
    for line in shared.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            shared_lines.append(stripped.lstrip(">").strip())
    shared_direction = " ".join(shared_lines)

    heading_re = re.compile(
        r"^###\s+\d+\.\s+(.+?)\s+—\s+`([^`]+\.svg)`\s*$",
        re.MULTILINE,
    )
    matches = list(heading_re.finditer(text[shared_end:]))
    badges = []
    raster_contract = (
        "STRICT FLAT SVG-STYLE ICON PROTOTYPE. Render at 1024x1024. "
        "The transport output is PNG, so place only the centered badge on a "
        "perfectly flat solid pure-white #FFFFFF background for local background "
        "removal. Every colored region must be one perfectly uniform flat fill. "
        "ABSOLUTELY NO gradients, lighting, shading, highlights, shadows, texture, "
        "glow, transparency effects, mockup, surrounding scene, border frame, "
        "text, letters, numbers, watermark, or raster noise. Use only the exact "
        "hex colors allowed below—no hue variations. Preserve clean geometric "
        "SVG-like shapes, medium-weight outlines, strong negative space, and "
        "instant readability at 30px. Follow exact requested object counts."
    )

    badge_section = text[shared_end:]
    for index, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(badge_section)
        body = badge_section[body_start:body_end]
        prompt_lines = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("## Export requirements"):
                break
            if stripped.startswith(">"):
                prompt_lines.append(stripped.lstrip(">").strip())
        badge_id = Path(match.group(2)).stem
        individual_prompt = " ".join(prompt_lines)
        prompt_lower = individual_prompt.lower()
        named_colors = [
            ("#60A5FA", ("easy", "blue")),
            ("#9B7BF7", ("moderate", "purple")),
            ("#F59E0B", ("hard", "amber")),
            ("#EC4899", ("exceptional", "pink")),
            ("#4ADE80", ("mint",)),
            ("#FB7185", ("coral",)),
        ]
        allowed = []
        for hex_color, keywords in named_colors:
            if any(keyword in prompt_lower for keyword in keywords):
                allowed.append(hex_color)
        for base_color in ("#171724", "#FFF8EC"):
            if base_color not in allowed:
                allowed.append(base_color)
        allowed = allowed[:5]
        palette = (
            "ALLOWED ARTWORK COLORS ONLY: %s, plus pure white only as the removable "
            "outer background. The first listed difficulty color is the dominant "
            "accent. Do not introduce any other color." % ", ".join(allowed)
        )
        prompt = " ".join(part for part in (
            raster_contract,
            palette,
            shared_direction.replace("transparent background", "transparent-ready outer background"),
            "Badge title for intent only (do not render it): %s." % match.group(1),
            individual_prompt,
        ) if part)
        badges.append({"id": badge_id, "title": match.group(1), "prompt": prompt})
    return badges


def download_to(prompt, out_path, width=200, height=200, seed=42, model=MODEL,
                timeout=90):
    """Generic download — saves the generated PNG to out_path.

    `model` overrides the image model for this call (default MODEL). `timeout`
    is the per-attempt response timeout in seconds. OG cards pass MODEL_OG
    ("gptimage") for the line-art design.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print("→ %s  (%dx%d)\n  %s..." % (out_path, width, height, prompt[:90]))

    if not KEY:
        print("  ERROR: POLLINATIONS_KEY not set in .env — cannot authenticate")
        return False

    # NOTE: User-Agent is REQUIRED — the API returns 403 without it.
    headers = {
        "Authorization": "Bearer %s" % KEY,
        "User-Agent":    "OreoBadge/1.0"
    }
    enc = urllib.parse.quote(prompt)
    url = "%s/%s?width=%d&height=%d&seed=%d&nologo=true&model=%s" % (
        BASE, enc, width, height, seed, model
    )

    for attempt in range(4):
        try:
            req  = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=timeout)
            data = resp.read()
            if len(data) < 1000:
                print("  WARN small (%d bytes), retry" % len(data))
                time.sleep(15 * (attempt + 1))
                continue
            out_path.write_bytes(data)
            print("  saved %d bytes  [model=%s]" % (len(data), model))
            return True
        except urllib.error.HTTPError as e:
            # Read the response body so we can show *why* the server refused.
            try:
                body = e.read().decode("utf-8", "replace").strip()
            except Exception:
                body = ""
            short = (body[:600] + "…") if len(body) > 600 else body

            # 401/403/400 won't fix themselves — bail fast with the full message.
            if e.code in (400, 401, 403, 404, 422):
                print("  FATAL HTTP %d %s   [model=%s]" % (e.code, e.reason, model))
                if body:
                    print("  ── server response ──")
                    for line in short.splitlines():
                        print("    " + line)
                    print("  ──────────────────────")
                else:
                    print("  (empty response body)")
                return False

            wait = 20 * (attempt + 1)
            print("  attempt %d HTTP %d %s — retry in %ds" %
                  (attempt + 1, e.code, e.reason, wait))
            if body:
                print("    server: " + short.splitlines()[0][:200])
            time.sleep(wait)
        except Exception as e:
            wait = 20 * (attempt + 1)
            print("  attempt %d error: %s — retry in %ds" % (attempt + 1, e, wait))
            time.sleep(wait)
    return False


def _generate_alpha_batch(prompts_dir, out_dir, only_names, seed, size, label,
                          nested=False, height=None, lock=False, force=False,
                          prompt_suffix=None):
    """Generate a folder of sticker-style PNGs with the cream-background
    transparency pass applied. Shared by stickers, website icons and brand
    marks — all want a flat cream background flood-filled to transparent.

    `size` is the canvas width; `height` defaults to `size` (square). Pass a
    different `height` for a non-square canvas (the brand lockup is 16:9).

    Two layouts:
      flat   (nested=False): prompts_dir/<name>.md          → out_dir/<name>.png
      nested (nested=True):  prompts_dir/<domain>/icon_prompt.md
                                                            → out_dir/<domain>.png
    `only_names` filters by name (stem, or domain folder when nested).

    Returns the number of prompts processed (0 if nothing to do).
    """
    if not prompts_dir.exists():
        print("No prompts directory at %s" % prompts_dir)
        return 0

    if nested:
        # One prompt per domain folder; the folder name is the asset name.
        mds = sorted(prompts_dir.glob("*/icon_prompt.md"))
        name_of = lambda m: m.parent.name
    else:
        # Flat: each <name>.md is one asset. Drop README.md if present.
        mds = sorted(prompts_dir.glob("*.md"))
        mds = [m for m in mds if m.stem.lower() != "readme"]
        name_of = lambda m: m.stem
    if only_names:
        mds = [m for m in mds if name_of(m) in only_names]
    if not mds:
        print("No %s prompt files in %s (after filtering)" % (label, prompts_dir))
        return 0

    h = height or size
    print("Generating %d %s(s)  [%dx%d, seed=%d]...\n" %
          (len(mds), label, size, h, seed))

    # Defer the transparency import so users without Pillow can still
    # run the icon/app generators. If it's unavailable we just warn
    # and skip the post-step — raw cream PNGs are still useful.
    try:
        from pipeline.sticker_transparency import make_transparent  # type: ignore
        _alpha_ok = True
    except Exception:
        try:
            # Direct path when generate_assets is invoked as a script
            # (pipeline/ isn't on sys.path).
            sys.path.insert(0, str(Path("pipeline").resolve()))
            from sticker_transparency import make_transparent  # type: ignore
            _alpha_ok = True
        except Exception as e:
            print("  warn: transparency pass unavailable (%s)" % e)
            print("        run `python pipeline/sticker_transparency.py` later")
            make_transparent = None  # type: ignore
            _alpha_ok = False

    for md in mds:
        prompt = _read_prompt(md)
        if not prompt:
            print("  SKIP %s — no ## Prompt block" % name_of(md))
            continue
        if prompt_suffix:
            prompt = prompt.rstrip()
            if not prompt.endswith(prompt_suffix):
                prompt = _normalize_sticker_prompt(prompt)
        out = out_dir / ("%s.png" % name_of(md))
        # Lock: once a good mark is committed, keep it. AI generation isn't
        # reproducible run-to-run, so a frozen brand mark stays put unless the
        # caller passes --force (or deletes the .png) to intentionally reroll.
        if lock and out.exists() and not force:
            print("  [locked] %s — keeping %s (pass --force to reroll)"
                  % (name_of(md), out.name))
            continue
        ok = download_to(prompt, out, width=size, height=h, seed=seed)
        # Auto-strip the warm-cream background as soon as the file
        # lands. Done per-asset (not in a final pass) so a
        # crash/interrupt mid-batch still leaves the already-generated
        # ones transparent. Fully in-place — same path overwritten.
        if ok and _alpha_ok and out.exists():
            try:
                make_transparent(out, out, tolerance=45)
                print("  alpha-stripped background")
            except Exception as e:
                print("  warn: transparency pass failed: %s" % e)
        time.sleep(8)
    return len(mds)


def generate_stickers(only_names=None, seed=42, size=1024):
    """Generate the printable-sheet stickers.

    Reads prompts/stickers/*.md and writes stickers/<stem>.png at
    `size`x`size` (default 1024). Different from icons/app sprites:
    these aren't device assets — they're print artwork that gets
    composited into a sheet by pipeline/compile_sticker_sheet.py.
    """
    n = _generate_alpha_batch(Path("prompts") / "stickers", Path("stickers"),
                              only_names, seed, size, "sticker",
                              prompt_suffix=STICKER_STYLE_SUFFIX)
    if n:
        print("\nDone. Run:  python pipeline/compile_sticker_sheet.py")


def generate_web_icons(only_names=None, seed=42, size=1024):
    """Generate the website service icons.

    Reads prompts/icons/<domain>/icon_prompt.md and writes
    branding/icons/web/<domain>.png. Sticker-style art on a flat cream
    background, run through the same transparency pass so they land
    transparent-ready for favicons / headers. Folders without an
    icon_prompt.md (e.g. the oreoOS app-icon set) are ignored.
    """
    n = _generate_alpha_batch(Path("prompts") / "icons",
                              Path("branding") / "icons" / "web",
                              only_names, seed, size, "web icon", nested=True)
    if n:
        print("\nDone. Transparent PNGs in branding/icons/web/")


def generate_blog_badges(only_names=None, seed=42, force=False, list_only=False):
    """Generate transparent LixBlogs badge prototypes with Pollinations Flux."""
    badges = _read_blog_badge_prompts()
    if not badges:
        print("No LixBlogs badge prompts found")
        return

    if list_only:
        for badge in badges:
            print("%-24s %s" % (badge["id"], badge["title"]))
        return

    if only_names:
        wanted = set(only_names)
        badges = [badge for badge in badges if badge["id"] in wanted]
        found = {badge["id"] for badge in badges}
        for missing in sorted(wanted - found):
            print("  ! unknown badge: %s" % missing)
    if not badges:
        print("No LixBlogs badges selected")
        return

    try:
        try:
            from pipeline.sticker_transparency import make_transparent  # type: ignore
        except Exception:
            sys.path.insert(0, str(Path("pipeline").resolve()))
            from sticker_transparency import make_transparent  # type: ignore
    except Exception as exc:
        print("Badge transparency pass unavailable (%s). Install Pillow first." % exc)
        return

    out_dir = Path("branding/icons/blogs.elixpo/blogs_badges")
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = 0
    print("Generating %d LixBlogs badge prototype(s)  "
          "[1024x1024, seed=%d, model=%s]%s...\n" %
          (len(badges), seed, MODEL_BLOG_BADGES,
           "  --force" if force else ""))

    for badge in badges:
        out = out_dir / (badge["id"] + ".png")
        if out.exists() and not force:
            print("  [locked] %s — keeping %s (pass --force to reroll)" %
                  (badge["id"], out.name))
            continue
        ok = download_to(badge["prompt"], out, width=1024, height=1024,
                         seed=seed, model=MODEL_BLOG_BADGES)
        if not ok:
            continue
        try:
            make_transparent(out, out, tolerance=24)
            print("  alpha-stripped flat white background")
        except Exception as exc:
            print("  warn: transparency pass failed for %s (%s)" %
                  (badge["id"], exc))
        generated += 1
        time.sleep(8)

    print("\nDone. Generated %d badge prototype(s) → %s" %
          (generated, out_dir))


def generate_brand(only_names=None, seed=OG_SEED, force=False):
    """Generate the brand marks (mascot mark, wordmark, lockup).

    Generated EXACTLY like the OG cards (see generate_og / OREO-LINEART.md), NOT
    the sticker pipeline — so the marks are line-art on the editorial card, with
    NO alpha-removal pass:

      1. AI renders the line-art DESIGN ONLY (16:9, text-free) → <name>.bg.png
      2. If the prompt has a `## Text` block, Pillow composites the fancy serif
         headline + the "Built in the Open" sub onto it → <name>.png; otherwise
         the design itself IS the final (e.g. the panda-only mascot mark).
      3. The intermediate .bg.png is deleted - the final <name>.png is kept.

    Reads prompts/brand/<variant>.md → branding/brand/<variant>.png.

    LOCKED: AI generation isn't reproducible, so a finished <name>.png is kept
    (the approved mark is frozen). Pass `force` (CLI: --force) or delete the .png
    to reroll. Seed defaults to OG_SEED (the proven line-art seed).
    """
    base = Path("prompts") / "brand"
    out_dir = Path("branding") / "brand"
    if not base.exists():
        print("No prompts directory at %s" % base)
        return

    mds = [m for m in sorted(base.glob("*.md")) if m.stem.lower() not in OG_SKIP]
    if only_names:
        mds = [m for m in mds if m.stem in only_names]
    if not mds:
        print("No brand prompt files in %s (after filtering)" % base)
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    print("Brand marks (%d)  [%dx%d, seed=%d, model=%s]%s...\n" %
          (len(mds), OG_W, OG_H, seed, MODEL_OG, "  --force" if force else ""))

    total = 0
    for md in mds:
        final = out_dir / ("%s.png" % md.stem)
        if final.exists() and not force:
            print("  [locked] %s — keeping %s (pass --force to reroll)"
                  % (md.stem, final.name))
            continue

        prompt = _read_prompt(md)
        if not prompt:
            print("  SKIP %s — no ## Prompt block" % md.stem)
            continue
        bg = out_dir / ("%s.bg.png" % md.stem)
        ok = download_to(prompt, bg, width=OG_W, height=OG_H, seed=seed, model=MODEL_OG)
        total += 1
        if ok and bg.exists():
            if "## Text" in md.read_text():
                _compose_og_text(md, bg, final)
                if final.exists():
                    try:
                        bg.unlink()
                    except OSError:
                        pass
            else:
                # No text to overlay - the line-art design IS the final mark.
                bg.replace(final)
                print("  design kept as %s (no ## Text)" % final.name)
        time.sleep(8)

    if total == 0:
        print("No new brand marks generated (existing ones are locked; --force to reroll).")
    else:
        print("\nDone. Brand marks → branding/brand/<variant>.png")


OG_SKIP = {"readme", "style", "palette"}


def generate_og(only=None, seed=42, force=False):
    """Generate open-graph / social cards, organised per site.

    Layout — prompt sources live per site under prompts/og/; the rendered
    images are written to branding/og/ (the generated-assets tree):

        prompts/og/<site>/prompts/<name>.md  →  branding/og/<site>/<name>.png

    Two-step, so the AI never has to render text:
      1. AI generates the text-free DESIGN (16:9) → a temporary <name>.bg.png
      2. Pillow composites the `## Text` → branding/og/<site>/<name>.png, then the
         intermediate .bg.png is DELETED — the final .png is the only artifact.

    LOCKED: AI generation is not reproducible run-to-run, so once <name>.png
    exists it is NOT regenerated (the approved panda is frozen). Pass `force`
    (CLI: --force) or delete the .png to intentionally reroll.

    Editorial tech-minimalism on the coral "oreo" palette: a faint dotted
    matrix, an entangled one-line Oreo, a couple of geometric shapes.
    Non-prompt files (README, STYLE, palette) are skipped automatically.

    `only` filters: the first token may be a <site> name (limit to that site);
    any remaining tokens are card stems (e.g. `["mails.elixpo", "default"]`).
    With no site token the remaining names filter cards across every site.

    Copy a site's branding/og/<site>/default.png → that app's public/og-image.png.
    Style spec: prompts/og/<site>/STYLE.md
    """
    base = Path("prompts") / "og"
    if not base.exists():
        print("No prompts directory at %s" % base)
        return

    sites = [d for d in sorted(base.iterdir()) if d.is_dir() and not d.name.startswith(".")]
    if not sites:
        print("No site folders under %s (expected e.g. %s/mails.elixpo/)" % (base, base))
        return

    # Split `only` into an optional leading site + trailing card stems.
    site_filter, card_filter = None, None
    if only:
        names = [s.name for s in sites]
        if only[0] in names:
            site_filter = only[0]
            card_filter = only[1:] or None
        else:
            card_filter = only

    total = 0
    for site in sites:
        if site_filter and site.name != site_filter:
            continue
        out_dir = Path("branding") / "og" / site.name
        mds = [m for m in sorted((site / "prompts").glob("*.md")) if m.stem.lower() not in OG_SKIP]
        if card_filter:
            mds = [m for m in mds if m.stem in card_filter]
        if not mds:
            continue

        out_dir.mkdir(parents=True, exist_ok=True)
        print("[%s] OG cards (%d)  [%dx%d, seed=%d, model=%s]%s...\n" %
              (site.name, len(mds), OG_W, OG_H, seed, MODEL_OG,
               "  --force" if force else ""))
        for md in mds:
            final = out_dir / ("%s.png" % md.stem)
            # LOCK: a finished card stays put. AI generation isn't reproducible
            # run-to-run, so once <name>.png exists we DON'T regenerate it —
            # the approved panda is frozen. Use --force (or delete the .png) to
            # intentionally reroll the design.
            if final.exists() and not force:
                print("  [locked] %s — keeping %s (pass --force to reroll)"
                      % (md.stem, final.name))
                continue

            prompt = _read_prompt(md)
            if not prompt:
                print("  SKIP %s — no ## Prompt block" % md.stem)
                continue
            bg = out_dir / ("%s.bg.png" % md.stem)
            ok = download_to(prompt, bg, width=OG_W, height=OG_H,
                             seed=seed, model=MODEL_OG)
            total += 1
            # Composite the text, then DELETE the intermediate design — the
            # final <name>.png is the single artifact we keep.
            if ok and bg.exists():
                _compose_og_text(md, bg, final)
                if final.exists():
                    try:
                        bg.unlink()
                        print("  cleaned intermediate %s" % bg.name)
                    except OSError:
                        pass
            time.sleep(8)

    if total == 0:
        print("No new OG cards generated (existing ones are locked; --force to reroll).")
    else:
        print("\nDone. Final cards → branding/og/<site>/<name>.png (intermediates removed). "
              "Copy branding/og/<site>/default.png → that app's public/og-image.png.")


def _compose_og_text(card_md, bg_path, out_path):
    """Overlay the card's `## Text` onto the AI design via pipeline/og_compose.py.
    Best-effort: warns and skips if Pillow or the composer is unavailable."""
    try:
        try:
            from pipeline.og_compose import compose_card  # type: ignore
        except Exception:
            sys.path.insert(0, str(Path("pipeline").resolve()))
            from og_compose import compose_card  # type: ignore
        compose_card(card_md, bg_path, out_path)
        print("  text composited → %s" % out_path)
    except Exception as e:
        print("  warn: text overlay skipped (%s)" % e)
        print("        run `python pipeline/og_compose.py` once Pillow is available")


def generate_outreach(site_name="blogs.elixpo", only_names=None, seed=OG_SEED,
                       force_art=False):
    """Generate reusable Oreo story art, then compose outreach cards locally.

    Unlike normal OG cards, the costly image output is deliberately retained:

      prompts/og/<site>/outreach/prompts/<name>.md
        → branding/og/<site>/outreach/stash/<name>.source.png  (locked raw)
        → branding/og/<site>/outreach/stash/<name>.art.png     (transparent)
        → branding/og/<site>/outreach/<name>.png              (local compose)

    Once the stash exists, ordinary reruns never call the image API. Use
    ``--force-art`` only when intentionally changing Oreo's story illustration.
    """
    prompt_dir = Path("prompts") / "og" / site_name / "outreach" / "prompts"
    output_dir = Path("branding") / "og" / site_name / "outreach"
    stash_dir = output_dir / "stash"
    if not prompt_dir.exists():
        print("No outreach prompts directory at %s" % prompt_dir)
        return

    mds = [path for path in sorted(prompt_dir.glob("*.md"))
           if path.stem.lower() not in OG_SKIP]
    if only_names:
        mds = [path for path in mds if path.stem in only_names]
    if not mds:
        print("No outreach prompt files selected in %s" % prompt_dir)
        return

    try:
        try:
            from pipeline.sticker_transparency import make_transparent  # type: ignore
            from pipeline.outreach_compose import compose_outreach_card  # type: ignore
        except Exception:
            sys.path.insert(0, str(Path("pipeline").resolve()))
            from sticker_transparency import make_transparent  # type: ignore
            from outreach_compose import compose_outreach_card  # type: ignore
    except Exception as exc:
        print("Outreach pipeline unavailable (%s). Install Pillow first." % exc)
        return

    stash_dir.mkdir(parents=True, exist_ok=True)
    print("[%s] outreach cards (%d)  [seed=%d, model=%s]%s...\n" %
          (site_name, len(mds), seed, MODEL_OG,
           "  --force-art" if force_art else ""))

    generated = 0
    composed = 0
    for md in mds:
        source = stash_dir / (md.stem + ".source.png")
        art = stash_dir / (md.stem + ".art.png")
        final = output_dir / (md.stem + ".png")
        generated_this_card = False

        if force_art or not source.exists():
            prompt = _read_prompt(md)
            if not prompt:
                print("  SKIP %s — no ## Prompt block" % md.stem)
                continue
            ok = download_to(prompt, source, width=768, height=768,
                             seed=seed, model=MODEL_OG)
            if not ok:
                continue
            generated += 1
            generated_this_card = True

        # Derive the transparent reusable layer locally. Rebuild it whenever
        # the source was deliberately rerolled, or if only the derived file is
        # missing. The raw source stays in stash for recovery and retuning.
        if force_art or not art.exists():
            make_transparent(source, art, tolerance=32)
            print("  stashed transparent art → %s" % art)

        compose_outreach_card(md, art, final)
        print("  composited locally → %s" % final)
        composed += 1
        if generated_this_card:
            time.sleep(8)

    print("\nDone. Generated %d new art layer(s); composited %d card(s)." %
          (generated, composed))
    print("Reusable art remains in %s" % stash_dir)


def generate_app(app_name, only_names=None, seed=42):
    """Generate all assets for one app: prompts/<app>/*.md → apps/<app>/assets/raw/*.png"""
    prompts_dir = Path("prompts") / app_name
    out_dir     = Path("apps") / app_name / "assets" / "raw"

    if not prompts_dir.exists():
        print("No prompts directory at %s" % prompts_dir)
        return

    mds = sorted(prompts_dir.glob("*.md"))
    if only_names:
        mds = [m for m in mds if m.stem in only_names]
    if not mds:
        print("No .md prompt files in %s" % prompts_dir)
        return

    print("Generating %d sprite(s) for app '%s'  [seed=%d]...\n" %
          (len(mds), app_name, seed))
    for md in mds:
        prompt = _read_prompt(md)
        if not prompt:
            print("  SKIP %s — no ## Prompt block" % md.name)
            continue
        out = out_dir / ("%s.png" % md.stem)
        download_to(prompt, out, width=200, height=200, seed=seed)
        time.sleep(8)
    print("\nDone. Run:  python pipeline/optimize_assets.py --app %s" % app_name)




# ── Active assets ──────────────────────────────────────────────────────────────
# Each entry: name → (width, height) or None to use default 200×200.
# Prompt text is read from prompts/<name>.md automatically.
# Comment out entries you don't want to regenerate.

ACTIVE = {
    # "home_bg":    (200, 200),
    # "apps_icon":  (200, 200),
    # "flappy_icon":  None,
    # "snake_icon":   None,
    # "gamepad_icon": None,
    # "commits_icon": None,
    # "settings_icon": None,
    # "bluetooth_icon": None,
    # "wifi_icon": None,
    # "about_icon": None,
    # "identity_icon": None,
    # "elixpo_pet_icon": None,
    # "elixpo_sketch_icon": None,
    # "IR_Quest_icon": None,
    # "commits_breaker_icon": None,
    # "wallpaper_icon": None,
    # "gallery_icon": None,
    # "flappy_panda_up":   None,
    # "flappy_panda_down": None,
}

# ── Inline fallback prompts (used if no .md file exists) ─────────────────────
# Edit the .md files in prompts/ instead — these are last-resort only.

_FALLBACK_PROMPTS = {}

# ── Style constants (appended to all prompts that don't have their own style) ─

PANDA_BASE = (
    "cute panda character with big eyes, black and white panda with pink cheeks, "
    "wearing a red badge with letter E on chest"
)

ICON_STYLE = (
    "pixel art cartoon style, thick dark outline, pastel vibrant colors, "
    "cute kawaii style, white background, square crop, no text, no watermark"
)

# ── Download ──────────────────────────────────────────────────────────────────

def download(name, width=200, height=200, seed=42):
    """Top-level icon: prompts/{name,icons/<name>}.md → branding/icons/raw/<name>.png."""
    prompt = (_read_prompt("prompts/%s.md" % name)
              or _read_prompt("prompts/icons/%s.md" % name)
              or _FALLBACK_PROMPTS.get(name))
    if not prompt:
        print("  SKIP %s — no prompt at prompts/%s.md or prompts/icons/%s.md"
              % (name, name, name))
        return
    download_to(prompt, "branding/icons/raw/%s.png" % name,
                width, height, seed=seed)


def _pop_seed(args):
    """Strip a `--seed N` pair from args. Returns (remaining_args, seed_int)."""
    seed = 42
    if "--seed" in args:
        i = args.index("--seed")
        if i + 1 < len(args):
            try:
                seed = int(args[i + 1])
            except ValueError:
                print("WARN: --seed expects an integer; using 42")
            args = args[:i] + args[i + 2:]
    return args, seed


def _pop_int_flag(args, flag):
    """Strip a `--flag N` pair from args. Returns (remaining_args, int or None)."""
    val = None
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            try:
                val = int(args[i + 1])
            except ValueError:
                print("WARN: %s expects an integer; ignoring" % flag)
            args = args[:i] + args[i + 2:]
    return args, val


def _lead_num(stem):
    """Leading number of a sticker stem ('021_coding' → 21, '01_hello' → 1)."""
    digits = ""
    for ch in stem:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else None


def _stickers_in_range(lo, hi):
    """Sticker stems whose leading number is within [lo, hi] (either may be None).

    Lets `--stickers --from 22` sweep every prompt from 022 onward without
    re-rendering the earlier ones.
    """
    out = []
    for m in sorted((Path("prompts") / "stickers").glob("*.md")):
        if m.stem.lower() == "readme":
            continue
        n = _lead_num(m.stem)
        if n is None:
            continue
        if lo is not None and n < lo:
            continue
        if hi is not None and n > hi:
            continue
        out.append(m.stem)
    return out


def main():
    args, seed = _pop_seed(sys.argv[1:])

    # ── LixBlogs creator badge prototypes ──────────────────────────────────
    # Parses all 25 prompts from the single strict SVG specification, renders
    # vector-style PNG sources with Flux, and removes the flat white background.
    if "--blog-badges" in args:
        force = "--force" in args
        list_only = "--list" in args
        args = [arg for arg in args if arg not in {"--force", "--list"}]
        idx = args.index("--blog-badges")
        only = args[idx + 1:]
        generate_blog_badges(only_names=only or None, seed=seed,
                             force=force, list_only=list_only)
        return

    # ── outreach social cards ────────────────────────────────────────────────
    # Generate the story illustration once, retain it in a stash, and freely
    # recompose the rest of the card with Pillow. Site defaults to blogs.elixpo.
    if "--outreach" in args:
        force_art = "--force-art" in args
        args = [arg for arg in args if arg != "--force-art"]
        idx = args.index("--outreach")
        rest = args[idx + 1:]
        site = "blogs.elixpo"
        if rest and (Path("prompts") / "og" / rest[0]).is_dir():
            site, *rest = rest
        outreach_seed = seed if "--seed" in sys.argv[1:] else OG_SEED
        generate_outreach(site_name=site, only_names=rest or None,
                          seed=outreach_seed, force_art=force_art)
        return

    # ── stickers mode ────────────────────────────────────────────────────────
    # Hardcoded 1024×1024 output. Any positional args after --stickers
    # are treated as stems to filter on (e.g. `--stickers 01_hello`),
    # mirroring the per-app mode's behaviour.
    if "--stickers" in args:
        # Optional range sweep: --from N / --to M select by leading number,
        # e.g. `--stickers --from 22` renders 022 onward. Otherwise any
        # positional args after --stickers are treated as exact stems.
        args, num_from = _pop_int_flag(args, "--from")
        args, num_to   = _pop_int_flag(args, "--to")
        idx  = args.index("--stickers")
        only = args[idx + 1:]
        if num_from is not None or num_to is not None:
            only = _stickers_in_range(num_from, num_to)
            if not only:
                print("No stickers in range from=%s to=%s" % (num_from, num_to))
                return
            print("Sweep: %d sticker(s) in range [%s..%s]" %
                  (len(only), num_from if num_from is not None else "start",
                   num_to if num_to is not None else "end"))
        generate_stickers(only_names=only or None, seed=seed)
        return

    # ── website icons mode ───────────────────────────────────────────────────
    # Sticker-style service icons → branding/icons/web/, transparency applied.
    # Positional args after --web filter by stem (e.g. `--web lixsketch`).
    if "--web" in args:
        idx  = args.index("--web")
        only = args[idx + 1:]
        generate_web_icons(only_names=only or None, seed=seed)
        return

    # ── brand marks mode ─────────────────────────────────────────────────────
    # Logo / wordmark / lockup → branding/brand/, OG-card style (line-art design
    # + composited fancy text, no alpha pass).
    # Positional args after --brand filter by variant (e.g. `--brand lockup`).
    # Seed defaults to OG_SEED (the proven line-art seed) unless --seed is passed.
    if "--brand" in args:
        force = "--force" in args
        args = [a for a in args if a != "--force"]
        idx  = args.index("--brand")
        only = args[idx + 1:]
        brand_seed = seed if "--seed" in sys.argv[1:] else OG_SEED
        generate_brand(only_names=only or None, seed=brand_seed, force=force)
        return

    # ── open-graph cards mode ────────────────────────────────────────────────
    # Editorial-minimalist social cards → og/, NO transparency pass.
    # Positional args after --og filter by stem (e.g. `--og default docs`).
    if "--og" in args:
        force = "--force" in args
        args = [a for a in args if a != "--force"]
        idx  = args.index("--og")
        only = args[idx + 1:]
        # Pin OG_SEED for the locked look unless the user explicitly overrides.
        og_seed = seed if "--seed" in sys.argv[1:] else OG_SEED
        generate_og(only=only or None, seed=og_seed, force=force)
        return

    # ── per-app mode ─────────────────────────────────────────────────────────
    if "--app" in args:
        idx  = args.index("--app")
        rest = args[idx + 1:]
        if not rest:
            print("Usage: generate_assets.py --app <app> [name ...] [--seed N]")
            return
        app, *only = rest
        generate_app(app, only_names=only or None, seed=seed)
        return

    # ── top-level icons mode ─────────────────────────────────────────────────
    targets = args
    active  = {k: v for k, v in ACTIVE.items()}
    if targets:
        active = {k: active.get(k, (200, 200)) for k in targets}
    if not active:
        print("No active entries. Uncomment entries in ACTIVE dict or pass names as args.")
        return

    print("Generating %d asset(s)  [seed=%d]...\n" % (len(active), seed))
    for name, dims in active.items():
        w, h = dims if dims else (200, 200)
        prompt = (_read_prompt("prompts/%s.md" % name)
                  or _read_prompt("prompts/icons/%s.md" % name)
                  or _FALLBACK_PROMPTS.get(name))
        if not prompt:
            print("  SKIP %s — no prompt at prompts/%s.md or prompts/icons/%s.md"
                  % (name, name, name))
            continue
        download_to(prompt, "branding/icons/raw/%s.png" % name, w, h, seed=seed)
        time.sleep(8)

    print("\nDone. Run:  python pipeline/optimize_assets.py")


if __name__ == "__main__":
    main()
