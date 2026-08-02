# LixBlogs outreach cards

These cards are for direct outreach and social distribution, not for the
`blogs.elixpo` website itself. Each generated Oreo story is retained as a
reusable transparent layer; the rest of the card is composed locally.

## Campaign set

| Card | Outreach idea | Oreo's visual action |
|---|---|---|
| `write` | Give a half-formed idea somewhere to live | Turning a loose thought-line into a page |
| `publish` | Make publishing feel quick and approachable | Sending a page through a portal into the open web |
| `share` | Turn a post into something easy to pass along | Launching a document as a paper plane |
| `recommend` | Direct recommendation to try LixBlogs | Gesturing toward an inviting browser doorway |
| `collaborate` | Invite a friend or teammate into the draft | Joining two page fragments with cursor-like shapes |
| `audience` | Show ideas travelling beyond the first reader | Watching one page ripple outward through connected circles |

## Production

Generate and review these one at a time:

```bash
python3 pipeline/generate_assets.py --outreach blogs.elixpo write
```

The first run creates both `stash/write.source.png` and the transparent
`stash/write.art.png`, then produces `write.png`. Later runs reuse the stash
and spend no image credits:

```bash
python3 pipeline/generate_assets.py --outreach blogs.elixpo write
```

To reroll Oreo intentionally with the same default seed (`7`):

```bash
python3 pipeline/generate_assets.py --outreach blogs.elixpo write --force-art
```

To iterate only the local card layout:

```bash
python3 pipeline/outreach_compose.py blogs.elixpo write
```

## Layout

- `prompts/write.md` is the active, API-ready story prompt.
- `ideas/` holds future story prompts until they are tuned for the reusable-art workflow.
- Generated sources and cutouts live in `branding/og/blogs.elixpo/outreach/stash/`.
- Final cards live in `branding/og/blogs.elixpo/outreach/`.
