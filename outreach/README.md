# Elixpo Outreach Studio

A dependency-free static GUI for composing brand outreach cards across the
entire Elixpo ecosystem—not only Elixpo Blogs. Use it for any product, launch,
event, announcement or community campaign. It has purpose-built layouts for
both 16:9 (1280×720) and 1:1 (1080×1080). All rendering happens in the browser
with Canvas; the app never calls an image API.

The interface uses the existing Elixpo wordmark from
`branding/brand/elixpo_word_mask_text.png`.

## Open the studio

Serve the repository root with any static server, then open `/outreach/`:

```bash
python3 -m http.server 8000
```

```text
http://localhost:8000/outreach/
```

Serving from the repository root lets the curated picker load assets from
`stickers/`. The upload control also works for new outreach stickers and does
not require updating a manifest.

## Workflow

1. Select a curated sticker, type any sticker filename from `stickers/`, or
   upload a new transparent PNG/WebP.
2. Edit the eyebrow, headline, description and URL.
3. Choose 16:9 or 1:1, then tune the palette, sticker size and placement.
4. Download the final PNG at the format's native resolution.

The **Tangy treatment** selector changes the actual graphic language—not only
the colors. Available treatments are Blob Party, Sunburst, Ribbon Rush,
Confetti Pop and Editorial Zest. Each has separate 16:9 and 1:1 positioning.

No generated output is written into the repository automatically—the browser
downloads it to the user's normal downloads folder. Move approved general
campaigns into `branding/outreach/`, or into the appropriate product's branding
folder when the card belongs to one Elixpo service.
