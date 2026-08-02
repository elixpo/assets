# Oreo — line-art edition (editorial OG system)

> **LOCKED reference.** This is the single source of truth for the
> **line-art Oreo** and the **editorial tech-minimalism OG cards**. It is the
> calm, grown-up counterpart to the pixel-art mascot in [`MASCOT.md`](MASCOT.md):
> same panda **Oreo**, same signature **red "E" chest badge**, rendered as one
> continuous line on a dotted-matrix card. Every OG/social asset — and anything
> inspired by this style — must respect this page. If a generated image
> contradicts it, the image is wrong, not the page.

---

## Identity at a glance

| | |
|---|---|
| **Who** | Oreo, the Elixpo panda |
| **Style** | Continuous **one-line drawing** — fine, single-weight vector line |
| **Vibe** | Editorial tech-minimalism — structured, intellectual, airy |
| **Personality** | Cute, **happy, healthy**, friendly, calm |
| **Used for** | OG / social cards, hero art, section dividers, slide backdrops |

The pixel-art Oreo (`MASCOT.md`) and this line-art Oreo are the **same
mascot** in two registers. Pick line-art for editorial / product surfaces;
pick pixel-art for playful / celebratory surfaces.

---

## The panda (locked spec)

- **One continuous, unbroken line** — a true continuous-line / one-line
  drawing (a single pen stroke that never lifts). **Very thin, fine,
  single-weight** strokes; a few gentle loops, loose and minimal. This is
  **LINE ART** — **never** a polished, accurately-rendered or filled
  illustration: no solid fills, no detailed/shaded face, no smooth cartoon.
- **Cute but minimal** — round, plump *in shape*; the face **suggested with a
  few simple strokes** (cute **gleamy, sparkling eyes** with a tiny white catch-light + a little smile), never a detailed
  rendered face. A relaxed sitting pose.
- **Head turned slightly toward the LEFT** (toward the headline) — a gentle
  three-quarter view, not full-front, not full-profile.
- **Fairly large and prominent** but kept on the **right ~40–42%** of the
  card, pushed to the right edge, **clear of the left text zone**.

### Colour on the mascot (the only saturated colour anywhere)

| Part | Colour | Hex |
|---|---|---|
| Both **ears** | Coral | `#ff7759` |
| **One leg** (filled) | Coral | `#ff7759` |
| **Chest "E" badge** | Mascot red | `#dc3c32` |
| Everything else (the line) | Ink | `#212121` |

The **"E" chest badge** is **mandatory** and makes the panda *Oreo*: a
**small, compact, perfectly round red `#dc3c32`** badge, **centred and
aligned** on the chest (only a fraction of the chest), carrying a single
clean, **bold, stylish letter "E"**. It is the **lone letter** allowed in the
whole design.

---

## The card (locked spec)

- **16:9, 1280×720, no cropping.** Flat 2D vector. NO 3D, gradients, glow,
  neon or shadows.
- **Background:** white `#ffffff` under a **faint dotted matrix** — an even
  field of tiny `#d9d9dd` dots (halftone / pegboard), subtle, receding.
- **Geometry:** **2–3** understated shapes — thin `#d9d9dd` hairline outlines
  (open circle / triangle / square / arc), framing the mascot, **never
  filled**, perfectly aligned like a design-system wireframe. **No coral** in
  the geometry — coral stays on the panda.
- **Left ~55% stays empty** in the AI image — the type is composited later.

### Palette (the "oreo" / Cohere system, light theme)

| Token | Hex | Role |
|---|---|---|
| Canvas | `#ffffff` | Background |
| Ink | `#212121` | The one-line panda + headline |
| Slate | `#75758a` | Sub copy |
| Muted slate | `#93939f` | Eyebrow / url |
| Hairline | `#d9d9dd` | Dotted matrix + geometry |
| **Coral** | `#ff7759` | Panda ears + one leg; headline underline |
| **Badge red** | `#dc3c32` | The panda's "E" chest badge |

### Type (composited by Pillow, never by the model)

- **Headline** — bold high-contrast **serif** (Fraunces / Playfair), ink.
- **Eyebrow / url** — **Space Mono**, uppercase, tracked, muted slate.
- **Sub** — Inter, slate.
- Heavy **coral underline** under the headline.

---

## Pipeline (locked)

```
1. AI renders the DESIGN ONLY  (gptimage, 16:9, NO text)        → temp <name>.bg.png
2. Pillow composites the type  (## Text block)                  → output/<name>.png
3. the temp .bg.png is DELETED — the final .png is the only kept artifact
```

- Generator: `pipeline/generate_assets.py --og <site> [card]`
- Compositor: `pipeline/og_compose.py <site> [card]`
- Prompts + per-site cards: `prompts/og/<site>/`
- **Locked:** AI runs vary, so a finished `output/<name>.png` is **never
  regenerated**. Reroll only with `--force` (or by deleting the `.png`). Seed
  is pinned (`OG_SEED`); `--seed` explores.

---

## Hard rules (do / don't)

### ✅ Do
- One continuous, **fine** line; a few gentle loops; clean and readable.
- Make Oreo **cute, happy and healthy**, head turned **slightly left**.
- Keep it **fairly large** but on the **right ~40–42%**, clear of the text.
- Coral **ears + one leg**; a **small** round **red** "E" badge, centred.
- Faint **dotted-matrix** background; 2–3 **hairline** geometric shapes.
- **16:9, no crop.** Let Pillow set all the type.

### ❌ Don't
- No dense scribble / heavy entanglement; no thick strokes.
- No sad, sickly or static look; no full-front or full-profile face.
- No coral in the geometry; no second letter or any other text in the design.
- No 3D, gradients, glow, neon, shadows, or a textured/closed-fill panda.
- Don't let the panda intrude into the left text zone.

---

## Inspired-by (creating the rest)

New surfaces inherit this page: keep the **one-line Oreo + dotted matrix +
hairline geometry + coral/red accents**, vary only the **composition** and the
`## Text`. To add a site, copy `prompts/og/mails.elixpo/` and edit its
`## Text`. For non-card surfaces (heroes, dividers), reuse the locked panda
spec above and drop the headline scaffold.
