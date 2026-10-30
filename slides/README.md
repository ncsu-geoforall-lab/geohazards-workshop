# Slides

The 20 minute context deck for the start of the workshop (`context.qmd`) and
the wrap-up deck (`wrapup.qmd`), built with Quarto revealjs in the GRASS theme
(`grass.scss`).

Render self-contained HTML files that work offline:

```bash
quarto render slides/context.qmd
quarto render slides/wrapup.qmd
```

The figures in `figures/` are committed, so rendering does not need the
workshop data. To rebuild them, run notebooks 01 to 04 in the workshop mapset,
then from the repo root inside the devcontainer:

```bash
uv run python slides/make_figures.py
```
