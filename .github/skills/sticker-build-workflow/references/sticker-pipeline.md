# Sticker Pipeline Reference

This repository uses a two-stage sticker workflow:

1. Generate square sticker art from markdown prompts.
2. Strip the outer white background and compile the results into print sheets.

## Source of Truth
- Prompt files: `prompts/stickers/<name>.md`
- Rendered stickers: `stickers/<name>.png`
- Print sheets: `stickers/sheet_XX.png`

## Required Sticker Format
Every sticker prompt should describe:
- Oreo's mascot identity
- The main subject or prop
- A warm cream padding band around the subject
- A pure white outer background outside the padding band
- Small accents that must stay inside the padding band
- A square, text-free, high-contrast pixel-art finish

## Recommended Prompt Pattern
Use a prompt structure like this:

- Start with the scene or pose
- Add the Oreo mascot clause
- State the cream padding band requirement
- State the white outer background requirement
- State where confetti, sparkles, motion marks, or other accents must remain
- End with the style suffix

## Variety Matrix
For a batch of stickers, vary one or more of these axes:

| Axis | Examples |
|---|---|
| Pose | standing, sitting, waving, saluting, jumping, dancing, holding |
| Prop | flag, rosette, badge, kite, lantern, snack, torch, medallion |
| Composition | badge crop, centered mascot, mascot above base object, diagonal motion pose |
| Energy | proud, playful, festive, ceremonial, cozy, energetic |
| Silhouette | round badge, compact icon, low pedestal, symmetric frame |

Do not vary everything at once. Strong sticker families usually keep one pose family and one layout family while rotating props or expressive details.

## Generation Commands
Use the repository venv for generation:

```bash
./venv/bin/python pipeline/generate_assets.py --stickers <name>
./venv/bin/python pipeline/generate_assets.py --stickers --from 149 --to 159
```

If a single asset needs rerendering:

```bash
./venv/bin/python pipeline/generate_assets.py --stickers <name> --force
```

## Transparency Rules
- The transparency pass should remove only the pure white outer background.
- The cream padding band should remain visible in the art before sheet compilation.
- If the white removal eats into the mascot or the padding band, the prompt is too close to the edge or the tolerance is too high.
- If the outer white remains visible, lower the tolerance only enough to preserve the cream band.

## Print Sheet Rules
- Use `python pipeline/compile_sticker_sheet.py` after the PNGs are ready.
- The default sheet is 8 x 12 inches at 300 DPI.
- The compiler arranges stickers in filename order.
- The compiler should preserve the transparent outer area and keep the sticker art sharp.

## Prompt Quality Notes
- Use explicit pixel-art language when the sticker should look retro or blocky.
- Use simple, high-contrast shapes.
- Keep confetti, sparkles, and motion lines inside the cream band.
- Avoid placing large props on the outer edge.
- Prefer a centered composition with clear breathing room.
