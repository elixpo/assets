# LixBlogs badge shared generation style

This block is prepended automatically to every prompt in `prompts/` by
`pipeline/generate_blog_badges.py`.

## Prompt

Create one original LixBlogs creator-achievement token with the compact,
collectible clarity of a modern platform badge system. The artwork must be
unmistakably Oreo and Elixpo, never a copy of another platform.

Render a crisp flat SVG-style icon prototype in a centered square composition.
Use the same locked Oreo medallion frame for every badge: two round ink panda
ears at the top, a warm-cream circular body with a thick ink contour, an inset
difficulty-colored tier ring, two small coral cheek dots, and a small red round
E-seal centered at the bottom. The seal contains the only permitted letter: one
simple cream E. Do not draw a full panda face or full panda character.

The unique achievement pictogram must be the dominant central symbol. Use bold
geometric shapes, rounded joins, medium-weight outlines, generous negative
space, and no more than three supporting motifs. It must remain recognizable at
30px. Keep a safe gap between the pictogram, tier ring, cheeks, ears and E-seal.

Locked palette: Oreo ink #262630, Oreo cream #F0EEE8, cheek coral #FF5D68,
E-seal red #DC3C32, plus exactly one tier accent chosen by the badge prompt:
Easy sky blue #60A5FA, Moderate purple #9B7BF7, Hard amber #F59E0B, or
Exceptional pink #EC4899. Use no tints, extra hues, authored opacity or color
variations.

Flat fills only. Absolutely no gradients, lighting, gloss, shadows, bevels,
texture, noise, transparency effects, 3D, photorealism, metallic finish,
mockup, surrounding scene, text, words, numbers, extra letters, watermark, or
third-party branding. Exceptional badges use a double tier ring and may use up
to three sparks; every other tier uses one ring and at most one spark.

Pollinations returns a raster image, so render the badge alone on a perfectly
flat, solid pure-white #FFFFFF outer background for local flood-fill removal.
No shadow or decoration may touch the background. Keep the badge fully inside
the canvas with generous padding and crisp closed edges.
