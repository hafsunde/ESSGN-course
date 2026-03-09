# Minimal Quarto + reveal.js + Manim Example

This project is a beginner-friendly scaffold for making lecture slides in Quarto and embedding a Manim animation.

## What this teaches

- How to render a reveal.js slide deck with Quarto
- How to render a Manim scene to MP4
- How to embed that MP4 in a Quarto slide with a relative path
- How to explain the identity

\[
\mathrm{Var}(X+Y)=\mathrm{Var}(X)+\mathrm{Var}(Y)+2\,\mathrm{Cov}(X,Y)
\]

## File structure

- `slides.qmd`
  - Quarto source for the reveal.js deck (title, formula slide, video slide, summary slide).
- `manim/variance_sum.py`
  - Manim Community Edition scene that animates the covariance-matrix argument step by step.
- `assets/variance_sum.mp4`
  - Final video file used by the slides (you generate this from Manim output).

## Prerequisites (brief)

1. Install **Quarto** (desktop CLI)
   - Verify: `quarto --version`
2. Install **Python 3.10+**
   - Verify: `python --version`
3. Install **Manim Community Edition** and dependencies
   - Command: `python -m pip install manim`
   - Verify: `python -m manim --version`

Note: Manim also needs system tools like `ffmpeg` and a LaTeX engine for MathTex.

## Build steps

Run these commands from the project root (`variance-sum-quarto-manim`).

1. Render the Manim animation to MP4 (1280x720, 30 fps):

```powershell
python -m manim --format=mp4 --fps 30 -r 1280,720 manim/variance_sum.py VarianceOfSumScene
python -m manim --format=mp4 --fps 30 -r 1280,720 manim/behavioral_genetics_bias.py BehavioralGeneticsBiasScene
py -m manim --format=mp4 --fps 30 -r 1280,720 manim/ld_score_visualization.py LDScoreVisualization   
```

Expected output file:

`media/videos/variance_sum/720p30/VarianceOfSumScene.mp4`

2. Copy the rendered MP4 into `assets/` with the exact name the slides expect:

```powershell
Copy-Item media/videos/variance_sum/720p30/VarianceOfSumScene.mp4 assets/variance_sum.mp4
```

3. Render the Quarto reveal.js slides:

```powershell
quarto render slides.qmd --to revealjs
quarto render behavioral_genetics.qmd --to revealjs
```

Output is typically a `slides.html` file in this folder.

## Troubleshooting (common beginner issues)

- `quarto` not found:
  - Quarto is not on your PATH. Reinstall Quarto or restart terminal after install.
- Manim install errors on Windows:
  - Update pip first: `python -m pip install --upgrade pip`
  - Re-run: `python -m pip install manim`
- `ffmpeg` missing:
  - Install ffmpeg and ensure `ffmpeg` works in terminal (`ffmpeg -version`).
- LaTeX-related MathTex errors:
  - Install a LaTeX distribution (for example MiKTeX on Windows), then retry render.

## Why relative paths matter

`slides.qmd` references `assets/variance_sum.mp4`. Keeping that exact path stable makes the deck portable and reproducible.
