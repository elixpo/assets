# LixBlogs creator badges

The 25 badge prompts live individually under `prompts/`. `STYLE.md` contains
the locked Oreo/Elixpo badge frame and is prepended to every prompt at runtime.

## Generate

```bash
python3 pipeline/generate_blog_badges.py --list
python3 pipeline/generate_blog_badges.py first-light
python3 pipeline/generate_blog_badges.py first-light finding-a-voice
python3 pipeline/generate_blog_badges.py             # all prompts
python3 pipeline/generate_blog_badges.py first-light --force
python3 pipeline/generate_blog_badges.py first-light --seed 7 --force
```

The generator uses Pollinations `model=klein`, renders 1024×1024 source PNGs,
removes the flat white background locally, and saves finished assets to:

```text
branding/icons/blogs.elixpo/blogs_badges/<badge-id>.png
```

Existing outputs are locked. A normal rerun skips them; use `--force` only for
an intentional reroll. Every badge gets a stable unique seed derived from its
badge ID and the `--seed` base, so generating a badge alone matches its batch
result while different badges do not share the same seed. The PNGs are Klein
prototypes. The original
`badges_prompt.md` remains the strict reference for hand-authored production
SVG exports.
