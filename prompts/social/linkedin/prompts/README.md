# LinkedIn generation prompts

Each asset has a `## Config` block and a `## Prompt` block. Generate them with:

```bash
python3 pipeline/generate_linkedin_assets.py --list
python3 pipeline/generate_linkedin_assets.py profile
python3 pipeline/generate_linkedin_assets.py banner
python3 pipeline/generate_linkedin_assets.py          # both
python3 pipeline/generate_linkedin_assets.py banner --force
```

Existing outputs are locked unless `--force` is supplied.
