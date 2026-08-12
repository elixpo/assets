# OG style — Agent Elixpo

Agent Elixpo follows the shared Oreo editorial-tech OG system documented in
`prompts/og/README.md`: a text-free 16:9 generated design on a faint dotted
matrix, with exact typography composited later by `pipeline/og_compose.py`.

The Agent-specific visual language is a restrained orchestration flow: one
blank issue card, one three-node branch, and one completion-check circle. These
are extremely pale `#d9d9dd` background scaffolds with a fraction of Oreo's
visual weight, never dark foreground icons, props, or extra mascot limbs.

The mascot is the approved line-art Oreo from the canonical Blogs OG—not a new
model interpretation. `pipeline/og_compose.py` crops that known-good artwork,
removes its light background, scales it to the `## Layout` box, anchors it on
the right, draws the pale Agent workflow geometry, and creates the dotted
canvas. Agent OG generation is therefore local and deterministic.
Keep the face controlled rather than tangled: two equal aligned oval eyes with
one matching catch-light each, a centred tiny nose, and a calm closed smile.
Outer-body looseness must never distort Oreo's gaze or expression.

The Pillow compositor—not the image prompt—keeps the left side empty. Oreo and
the orchestration path are mechanically constrained to the far right, using only
ink `#212121`, hairline `#d9d9dd`, coral `#ff7759`, and the red `#dc3c32` E
badge on white.
