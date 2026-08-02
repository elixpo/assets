# Elixpo LinkedIn identity assets

Production prompts and layout rules for Elixpo's LinkedIn presence. These assets
represent the whole Elixpo open-source ecosystem, not one product.

The visual direction is a clean, credible developer-community platform with the
bright, youthful energy of Elixpo's **Tangy** outreach system. It may borrow the
clarity, whitespace and community-forward confidence associated with platforms
like Kaggle, but must not copy Kaggle's logo, typography, colours or interface.

## Locked identity

- Oreo is Elixpo's round panda mascot.
- Oreo uses fine `#212121` line art on white, with coral `#ff7759` ears and one
  coral leg.
- A small round `#dc3c32` chest badge contains the only model-rendered letter:
  a clean white **E**.
- Canvas: warm white `#fffcf7` or pure white `#ffffff`.
- Supporting colours: peach `#ffdec7`, blush `#ffcdd3`, sunny yellow `#ffdd70`,
  pale grey `#d9d9dd`, slate `#686879`.
- Background texture: a quiet, precise matrix of tiny pale-grey dots.
- Style: flat editorial vector art; clever, optimistic, youthful and technical.
- Never use 3D, photorealism, gradients, glow, neon, drop shadows, glass effects,
  generic corporate people, stock imagery or a glossy cartoon render.

Use the existing approved identity assets when compositing:

- `branding/brand/mascot_elixpo_oreo.png`
- `branding/brand/elixpo_word_mask_text.png`
- `branding/brand/elixpo_lock_up_text_mascot.png`

Do not ask an image model to redraw the Elixpo wordmark. Where a wordmark or
tagline is required, add the approved PNG or crisp local typography afterward.

---

## 1:1 LinkedIn profile image

**Master size:** 1080x1080 px, RGB PNG. LinkedIn displays profile images through
a circular crop, so all essential content must remain inside a centred circle
with a diameter no larger than 820 px. Check the result at 64 px and 32 px.

### Generation prompt

Create a square 1:1 brand-avatar background, exactly 1080x1080 pixels, for the
official Elixpo LinkedIn page. Clean developer-community identity with generous
white space and a playful Gen-Z editorial edge. Flat 2D vector only.

Place Oreo, Elixpo's friendly round panda mascot, large and centred. Oreo is
drawn in confident, minimal, fine `#212121` line art: immediately readable at
tiny avatar size, expressive but not detailed. Both ears and one small lower-leg
shape are filled flat coral `#ff7759`. On the centre of the chest is a compact,
perfectly round `#dc3c32` badge containing one clean white capital letter **E**.
The E badge is the focal brand signal but does not overpower Oreo's face.

Behind Oreo, create one bold but restrained **Tangy halo**: an asymmetrical
peach `#ffdec7` organic blob, a small sunny-yellow `#ffdd70` circle, and one
short coral `#ff7759` capsule. Add two or three thin black editorial arcs or
spark marks to suggest curiosity, building and momentum. Use a warm-white
`#fffcf7` canvas with an extremely subtle, evenly spaced `#d9d9dd` dotted grid.
The result should feel like an open-source community badge: smart, memorable,
welcoming and slightly mischievous.

Keep Oreo and every important Tangy shape inside the central 76% of the square.
Maintain strong silhouette separation and ample breathing room. The composition
must survive a circular crop with no clipped ears, badge or face.

**CRITICAL TEXT RULE:** no words, captions, slogans, extra letters or numbers.
The single white **E** inside Oreo's red chest badge is the only permitted text.
No borders, frames, mockups, UI, logos from other brands or watermark.

### Recommended production method

Prefer local composition over generation: centre
`branding/brand/mascot_elixpo_oreo.png` above a Tangy halo rendered as vector or
Canvas shapes. This preserves the approved Oreo exactly and costs no generation
credits. Use the prompt only if a new avatar illustration is intentionally
required.

---

## 4:1 LinkedIn page banner

**Master size:** 1600x400 px, RGB PNG. Keep the central story within a 1440x320
safe region. Reserve the lower-left corner because LinkedIn's page avatar may
cover it at some viewport sizes. Keep important artwork and all text at least
80 px from every edge.

### Generation prompt — artwork layer only

Create an ultra-wide 4:1 LinkedIn company-page banner background, exactly
1600x400 pixels, for Elixpo: an open-source ecosystem built as a university
project series by a group of teen developers. The banner should communicate
curiosity, collaboration, practical building and open-source momentum. Clean,
credible developer-community platform design with youthful Tangy energy;
editorial and intelligent rather than childish. Flat 2D vector only.

Use a warm-white `#fffcf7` background with a subtle edge-to-edge matrix of tiny
`#d9d9dd` dots. Build a left-to-right visual story across the canvas using a
single fine `#212121` line: a loose code bracket flows into connected nodes,
then a tiny sprout, a paper plane and an open path continuing beyond the right
edge. The story should read as **idea -> build -> share -> grow**, with only a
few elegant marks and large areas of calm negative space.

Keep the LEFT 58% mostly open for the approved Elixpo lockup and copy added in
post. Place Oreo in the RIGHT 30%, between approximately x=1120 and x=1480,
facing left toward the future text. Oreo is the friendly, round Elixpo panda in
minimal fine `#212121` line art, leaning forward with one paw guiding a small
coral paper plane into the open path. Both ears and one leg use flat coral
`#ff7759`; the small round chest badge is `#dc3c32` with one clean white **E**.

Add a restrained **Tangy trail** around the right-hand story: one large pale
peach `#ffdec7` organic blob behind Oreo, one blush `#ffcdd3` pill, one sunny
yellow `#ffdd70` circle, and two short coral `#ff7759` motion marks. Shapes may
peek through or partially exit the top and right edges, creating lively depth
without clutter. Preserve crisp contrast around Oreo's face and badge.

The whole banner should feel welcoming, technically capable and community-led:
a space where young builders learn in public and ship open-source work together.
Use asymmetry, deliberate whitespace and a clear visual rhythm suitable for a
professional LinkedIn page.

**CRITICAL TEXT RULE:** render no words, slogans, captions, code, numbers or
extra letters. The white **E** inside Oreo's red badge is the only permitted
letter. Do not generate the Elixpo wordmark. No UI screenshots, fake browser
windows, laptop mockups, third-party logos, watermark, gradients, 3D, glow,
shadows, photorealism or stock characters.

### Deterministic overlay after generation

Add the approved lockup or wordmark in the open left region. Suggested copy:

```text
ELIXPO
Build curious things. Share them in the open.
Open source · Teen-built · Community-driven
```

Composition guidance:

- Place the approved Elixpo wordmark around x=150, y=95, with a maximum width
  of 360 px.
- Place the main line below it in a bold editorial serif or the repository's
  established headline font; keep it to one or two lines.
- Set the supporting line in a clean sans or mono face with generous tracking.
- Use `#212121` for primary copy, `#686879` for supporting copy and a short
  `#ff7759` underline or capsule as the only typographic accent.
- Do not place essential text below y=320 or left of x=120.
- If the page avatar obscures the lower-left corner in a preview, move the text
  group right; never shrink the main statement below comfortable reading size.

### Export checks

1. Preview the square avatar through a circle at 1080, 128, 64 and 32 px.
2. Preview the banner at full width and at a narrow/mobile crop.
3. Confirm all typography is composited, not model-generated.
4. Confirm there is exactly one E on each asset and it belongs to Oreo's badge.
5. Confirm no Tangy decoration competes with Oreo's face or the banner copy.
6. Export clean RGB PNG files without metadata-heavy editor layers.

