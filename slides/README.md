# Context slides

The 20 minute context deck for the start of the workshop, built with Quarto
revealjs in the GRASS theme (`grass.scss`).

Render a self-contained HTML file that works offline:

```bash
quarto render slides/context.qmd
```

The figures in `figures/` are committed, so rendering does not need the
workshop data. To rebuild them, run notebooks 01 to 04 in the workshop mapset,
then from the repo root inside the devcontainer:

```bash
uv run python slides/make_figures.py
```
