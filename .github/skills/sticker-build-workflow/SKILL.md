---
name: sticker-build-workflow
description: 'Build Oreo sticker assets for this repo. Use for sticker prompt files, pixel-art sticker generation, transparency cleanup, batch variety planning, and print-sheet compilation.'
user-invocable: false
---

# Sticker Build Workflow

Use this skill when creating, editing, generating, cleaning, or batching Oreo sticker assets in this repository.

## What This Workflow Covers
- Sticker prompt files in `prompts/stickers/*.md`
- Generated sticker PNGs in `stickers/*.png`
- Transparency cleanup for generated stickers
- Print-sheet compilation
- High-quality, pixel-art-first variation planning

## Canonical Sticker Spec
- Source prompts live in `prompts/stickers/<name>.md`.
- Each prompt file defines one sticker asset.
- Target render size is `1024x1024`.
- Output files are written to `stickers/<name>.png`.
- Sticker art must stay on Oreo's brand palette and canonical anatomy.
- Sticker finish uses a two-tone background model: a warm cream padding band around the subject and a pure white outer background that gets stripped to transparency.

## When to Use
- Adding a new sticker concept
- Revising an existing sticker prompt
- Generating one sticker or a batch of stickers
- Fixing padding, edge bleed, or transparency artifacts
- Compiling finished stickers into print sheets
- Making a sticker batch feel more visually varied while staying on-brand

## Core Rules
1. Keep every sticker square and text-free.
2. Use Oreo's mascot rules from `references/MASCOT.md` and the sticker palette.
3. Keep the main subject centered inside a visible 3-5 px cream padding band.
4. Put the pure white outer background outside that padding band so flood-fill can strip only the outer area.
5. Keep sparkles, confetti, motion marks, and small props inside the cream band.
6. Avoid thin elements touching the outer edge.
7. Prefer crisp, blocky, pixel-art silhouettes over soft shapes.
8. Use a clear focal hierarchy: mascot first, prop second, accents third.

## Variety Rules
When generating a sticker batch, vary the concept along one or more of these dimensions:
- Pose: standing, sitting, jumping, waving, saluting, holding, dancing
- Prop: badge, flag, rosette, kite, lantern, snack, torch, medallion
- Composition: centered portrait, low base with mascot above, badge-style circle, diagonal motion pose, compact icon
- Emotional tone: proud, playful, celebratory, cozy, energetic, ceremonial
- Framing: close crop, badge crop, low pedestal, open space above, symmetrical composition

For consistency, only change a few dimensions at once. Do not introduce a new pose, a new prop, and a new composition style in the same batch unless the prompt explicitly needs a major variation.

## Generation Procedure
1. Decide the sticker theme and variety target.
2. Create or update the prompt markdown file in `prompts/stickers/`.
3. Make sure the prompt includes:
   - the Oreo mascot clause
   - the cream padding band
   - the white outer background
   - explicit instructions to keep tiny accents inside the cream band
4. Run the generator with the repo venv:
   - `./venv/bin/python pipeline/generate_assets.py --stickers <name>`
   - `./venv/bin/python pipeline/generate_assets.py --stickers --from <n> --to <m>`
5. If the transparency edge looks wrong, rerun the sticker transparency helper on the affected PNG and adjust tolerance only if needed.
6. Compile the finished set into a print sheet:
   - `python pipeline/compile_sticker_sheet.py`

## Quality Controls
- Prefer 8-bit pixel-art language when the sticker should look blocky or retro.
- If the generated art drifts toward painterly or smooth shapes, strengthen the prompt with explicit pixel-language: square pixels, chunky edges, stepped outlines, no gradients, no blur.
- If particles or confetti leak outside the subject area, tighten the prompt so they must stay inside the cream band.
- If a sticker becomes too busy, reduce the number of accents and make the silhouette simpler.
- If a sticker needs more breathing room, move the subject lower, smaller, or more centered rather than enlarging the outer elements.

## Output Validation
- Confirm the PNG exists in `stickers/`.
- Confirm the subject stays inside the cream band.
- Confirm transparency only removes the pure white outer background.
- Confirm the print sheet compiles without layout errors.

## Reference Files
- [Sticker prompt rules](./references/sticker-pipeline.md)
