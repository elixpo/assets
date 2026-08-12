# OreoLook OG style

OreoLook follows the canonical Elixpo OG system from
`prompts/og/blogs.elixpo/STYLE.md`: white dotted canvas, high-contrast serif
copy, coral underline, and minimal Oreo line art.

The mascot is the approved Oreo from the canonical Blogs OG, reused locally by
`pipeline/og_compose.py`. The Search variation adds only three whisper-light
`#e2e2e6` research motifs: a search lens, a query fanning into three sources,
and a synthesized answer card with citation dots. These remain background
scaffolding and never compete with Oreo or the typography.

The card is fully deterministic and does not invoke an image model. Pillow
crops, extracts, scales and positions the mascot, draws the search motifs and
composites the exact text.
