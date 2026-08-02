# LixBlogs outreach cards

These cards are for direct outreach and social distribution, not for the
`blogs.elixpo` website itself. They use the same locked Oreo line-art pipeline
as the site's OG card, but each illustration communicates one small action.

## Campaign set

| Card | Outreach idea | Oreo's visual action |
|---|---|---|
| `outreach-write` | Give a half-formed idea somewhere to live | Writing on a large floating page |
| `outreach-publish` | Make publishing feel quick and approachable | Sending a page through a portal into the open web |
| `outreach-share` | Turn a post into something easy to pass along | Launching a document as a paper plane |
| `outreach-recommend` | Direct recommendation to try LixBlogs | Gesturing toward an inviting browser doorway |
| `outreach-collaborate` | Invite a friend or teammate into the draft | Joining two page fragments with cursor-like shapes |
| `outreach-audience` | Show ideas travelling beyond the first reader | Watching one page ripple outward through connected circles |

## Production

Generate and review these one at a time. The normal OG command keeps the
approved final locked unless `--force` is passed:

```bash
python pipeline/generate_assets.py --og blogs.elixpo outreach-write
python pipeline/generate_assets.py --og blogs.elixpo outreach-publish
python pipeline/generate_assets.py --og blogs.elixpo outreach-share
python pipeline/generate_assets.py --og blogs.elixpo outreach-recommend
python pipeline/generate_assets.py --og blogs.elixpo outreach-collaborate
python pipeline/generate_assets.py --og blogs.elixpo outreach-audience
```

The model draws only the right-side artwork. `pipeline/og_compose.py` adds the
copy from each file's `## Text` block, preserving the existing 1280x720 card
layout and typography.
