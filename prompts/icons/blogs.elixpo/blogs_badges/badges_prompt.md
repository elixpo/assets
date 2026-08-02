# LixBlogs Creator Badge Icon Prompts

This document defines the visual direction and individual generation prompt for all 25 creator badge SVGs. The system borrows only the collectible clarity, compact silhouette, and instantly readable tiers associated with leading achievement platforms; its shapes, mascot cues, and visual language are original to Oreo and Elixpo. Save each finished asset under `public/badges/<badge-id>.svg` using the exact lowercase kebab-case filename listed in its heading.

## Shared SVG direction

Apply this direction to every individual badge prompt:

> Create an original LixBlogs creator-achievement token with collectible clarity: one consistent medallion silhouette, one bold central pictogram, and an immediately visible difficulty tier. Use only `viewBox="0 0 256 256"` on a transparent canvas. Every badge uses the same **Oreo medallion frame** defined below. The E-seal is the only letter allowed and must remain subordinate to the achievement pictogram. Build the unique central symbol from bold geometric shapes, rounded joins, consistent outlines, and generous negative space. It must read at 30px and feel friendly, clever, editorial, and unmistakably Elixpo. Do not imitate another platform's badge shapes or iconography. Use exactly the four locked Oreo colors plus the badge's one tier accent—never tints, opacity variants, or extra colors. Use flat fills only: no gradients, lighting, gloss, shadows, bevels, texture, noise, transparency effects, or 3D. Avoid all text, letters, and written numbers except the single E in the seal. Do not draw a full panda face or full panda character; the ears, cheek dots, cream-and-ink construction, and E-seal carry Oreo's identity. Do not use embedded raster images, filters, masks, clipping paths, patterns, external fonts, or external references. Include concise accessible `<title>` and `<desc>` elements.

## Locked badge anatomy

> Treat the frame as one reusable SVG component across all 25 badges. Draw in this back-to-front order: ears, cream body, tier ring, central pictogram, cheek dots, E-seal. Use these locked measurements:
>
> - two ink-filled circular ears, `r=24`, centered at `(76,48)` and `(180,48)`;
> - one cream body circle, `r=102`, centered at `(128,130)`, with an `8px` ink outline;
> - one inset tier ring centered at `(128,130)`, `r=91`, with a `10px` tier-colored stroke and no fill;
> - one central pictogram box from `(62,52)` to `(194,184)`; every unique symbol must remain inside it;
> - two coral cheek dots, `r=6`, centered at `(48,151)` and `(208,151)`, always above the pictogram layer and never moved;
> - one red E-seal circle, `r=19`, centered at `(128,218)`, with a `6px` ink outline and a simple cream E converted to a filled path.
>
> The ears may tuck behind the body but no artwork may cross the `20px` canvas safe area. Use `8px` as the standard visible outline width, rounded caps and joins, and never use a visible stroke below `6px`. Any isolated dot, cutout, spark, gap, or interior feature must be at least `10px` across in the 256-unit artwork. All cream pictogram shapes must have an ink outline so they remain distinct from the cream body. Easy, Moderate, and Hard badges use the single locked tier ring and no more than one spark. Exceptional badges replace that ring with two concentric pink strokes at `r=86` and `r=95`, each `6px` wide, and may use up to three sparks. Apart from this specified Exceptional ring substitution, only the tier accent and central pictogram may change. At 30px, recognition order must be pictogram first, tier second, Oreo identity third.

### Difficulty palette

| Difficulty | Primary accent |
| --- | --- |
| Easy | Sky blue `#60A5FA` |
| Moderate | Elixpo purple `#9B7BF7` |
| Hard | Achievement amber `#F59E0B` |
| Exceptional | Spotlight pink `#EC4899` |

Locked Oreo colors are ink `#262630`, cream `#F0EEE8`, cheek coral `#FF5D68`, and E-seal red `#DC3C32`.

### Small-size acceptance rules

- Judge the exported SVG at `30x30` first, without zooming. Reject it if the central achievement cannot be named from its silhouette.
- At 30px, no symbol may merge with the tier ring, cheeks, ears, or E-seal; keep at least `8` source units of clear space between those elements.
- Preserve the exact five-color palette. Anti-aliasing by the renderer is acceptable; authored opacity and additional fill or stroke colors are not.
- Prefer one dominant pictogram silhouette with no more than three supporting motifs. Exact counts stated in an individual prompt are mandatory.
- Never solve legibility with labels, initials, numerals, micro-lines, denser detail, or a larger central box.

## Badge prompts

### 1. First Light — `first-light.svg`

> Inside the locked Oreo medallion, design a rising Easy-blue sun emerging from the bottom edge of an open ink-and-cream notebook. Use exactly five broad rays and one tier-blue sparkle that meets the locked minimum feature size to suggest the creator's first published story. Keep the notebook and sunrise fused into one compact central silhouette; the Easy ring remains clearly visible around it.

### 2. Finding a Voice — `finding-a-voice.svg`

> Inside the locked Oreo medallion, design a friendly ink-and-cream editorial megaphone emitting exactly three progressively larger Easy-blue speech waves. Place one blue sparkle, at the locked minimum feature size, at the final wave to represent a creator developing their voice. Avoid musical notes, characters, and generic loudspeaker warning imagery.

### 3. Profile Complete — `profile-complete.svg`

> Inside the locked Oreo medallion, design a compact profile card with a simplified Oreo-ear portrait silhouette, one small banner strip, two short non-text bio strokes, and a prominent Easy-blue completion check. Make it feel like a finished creator identity rather than a generic user icon.

### 4. Topic Explorer — `topic-explorer.svg`

> Inside the locked Oreo medallion, design a compact Easy-blue compass whose three primary points terminate in a leaf, a code-bracket shape, and a small star. Keep all three topic symbols geometric and bold enough to survive at 30px.

### 5. Series Starter — `series-starter.svg`

> Inside the locked Oreo medallion, design exactly three stacked cream editorial cards connected by one Easy-blue curved binding line. Give the top card one blue bookmark tab and one tiny sparkle, communicating the start of a connected story collection.

### 6. Ten Stories — `ten-stories.svg`

> Inside the locked Oreo medallion, design a substantial fan of cream manuscript pages with ten page edges implied through exactly five paired ink cuts, never a written number. Keep every cut at or above the locked minimum gap size. Wrap one Moderate-purple ribbon around the stack to mark the milestone.

### 7. Prolific Creator — `prolific-creator.svg`

> Inside the locked Oreo medallion, design an abundant compact library of bold ink-and-cream book spines, with one Hard-amber fountain pen rising from the center like a torch. Keep the silhouette prestigious but playful, with no shelf labels.

### 8. Deep Diver — `deep-diver.svg`

> Inside the locked Oreo medallion, design one ink fountain-pen nib diving beneath two stylized Hard-amber wave bands toward a small cream pearl. Use a simple descending trail without numbers; communicate long-form depth and discovery using flat geometry only, never glow.

### 9. Consistent Creator — `consistent-creator.svg`

> Inside the locked Oreo medallion, design a compact ink-and-cream calendar grid with exactly four separated week rows completed by small Moderate-purple dots. Wrap one continuous purple orbit around the calendar to symbolize reliable publishing.

### 10. Unbroken Voice — `unbroken-voice.svg`

> Inside the locked Oreo medallion with its Exceptional double ring, design one uninterrupted flat pink waveform looping through a compact twelve-segment ink progress ring wholly contained in the central pictogram box. Place one fountain-pen nib at the waveform's origin. Keep all twelve segments broad and visibly separated at 30px. Use no glow; the unbroken geometry itself communicates endurance.

### 11. First Hundred — `first-hundred.svg`

> Inside the locked Oreo medallion, design a central open cream story surrounded by an orderly semicircle of Easy-blue reader dots in three sizes. Add one upward blue spark above the book. Do not show `100`, text, or literal people.

### 12. Reader Favourite — `reader-favourite.svg`

> Inside the locked Oreo medallion, design an open cream book whose pages form a heart only through central negative space. Add a small halo of Moderate-purple reader dots and one purple bookmark ribbon. Keep it editorial, not a generic social-media heart button.

### 13. Wide Reach — `wide-reach.svg`

> Inside the locked Oreo medallion, design an ink globe made from curved page lines, with exactly three Hard-amber broadcast arcs carrying tiny cream story cards toward different regions. Keep the globe open and readable rather than densely mapped.

### 14. Headliner — `headliner.svg`

> Inside the locked Oreo medallion with its Exceptional double ring, design one prominent cream story card beneath a flat pink spotlight cone. Frame it with two outward broadcast waves and exactly three crown-like pink sparks. Use no headline or text.

### 15. Worth Saving — `worth-saving.svg`

> Inside the locked Oreo medallion, design one tier-purple bookmark ribbon inserted into an open cream book, with exactly three smaller tier-purple tabs orbiting toward it. Cut one sparkle, at the locked minimum feature size, from the main ribbon using negative space. Do not introduce a darker purple.

### 16. Shareworthy — `shareworthy.svg`

> Inside the locked Oreo medallion, design one cream story card splitting into exactly three clean Hard-amber outward paths, each ending in a small reader node. Add one moving spark to the longest path. Avoid upload arrows and social-network logos.

### 17. Read to the End — `read-to-the-end.svg`

> Inside the locked Oreo medallion with its Exceptional double ring, design an open cream book whose page trail reaches a flat pink finish ribbon and bold pink completion check. Enclose the scene with an almost-complete ink progress arc; use no secondary mint color.

### 18. Returning Audience — `returning-audience.svg`

> Inside the locked Oreo medallion, design exactly three small ink reader nodes following one looping Hard-amber path back toward an open cream story. Shape the center page like a simple doorway to suggest repeated return.

### 19. First Collaboration — `first-collaboration.svg`

> Inside the locked Oreo medallion, design exactly two balanced fountain pens meeting nib-to-nib above one shared cream page. Use Easy blue on one pen and cream with ink on the other; place one blue sparkle exactly at the connection to communicate equal co-authorship.

### 20. Creative Partner — `creative-partner.svg`

> Inside the locked Oreo medallion, design exactly three creator nodes in a balanced triangle, connected by Moderate-purple editorial strokes that merge into one finished cream story card. Place one shared sparkle at the merge point.

### 21. Team Player — `team-player.svg`

> Inside the locked Oreo medallion, design a circular group of exactly four simplified creator nodes around one central open cream publication. Connect every node to the publication with `6px` Hard-amber lines, forming one cohesive team emblem.

### 22. Conversation Starter — `conversation-starter.svg`

> Inside the locked Oreo medallion, design an open cream story emitting exactly three overlapping ink speech bubbles that expand outward. Put small Hard-amber reader dots inside the two outer bubbles and one amber spark at the origin.

### 23. Present Author — `present-author.svg`

> Inside the locked Oreo medallion, design one fountain pen actively replying inside a large Moderate-purple speech bubble. Connect it with one curved return path to exactly two smaller discussion bubbles. Avoid generic reply UI icons.

### 24. Publication Builder — `publication-builder.svg`

> Inside the locked Oreo medallion, design a compact publication building made from stacked cream story pages, with exactly three creator nodes placing the final top page together. Add one Hard-amber flag-shaped bookmark at the summit.

### 25. Staff Pick — `staff-pick.svg`

> Inside the locked Oreo medallion with its Exceptional double ring, design the collection's most prestigious symbol: a refined flat pink award ribbon surrounding one cream fountain-pen nib. Echo the frame's panda ears with a subtle crown arc and add exactly three restrained pink stars. Keep the red E-seal visible. It must feel curated and rare without words, initials, metallic effects, or glow.

## Export requirements

- Use `viewBox="0 0 256 256"`.
- Keep the background transparent.
- Do not set fixed `width` or `height` attributes.
- Do not use `currentColor`; each badge owns its palette.
- Do not use gradients, masks, clip paths, filters, patterns, or authored opacity.
- Do not include `<text>` except the single outlined E converted to paths inside the locked red E-seal. Do not include `<image>`, scripts, external fonts, or external references.
- Include concise, descriptive `<title>` and `<desc>` elements.
- Expand strokes when practical and optimize redundant groups and path points.
- Test every badge at 30px, 38px, 46px, and 96px in both light and dark themes.
