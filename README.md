# Multiphoton Microscopy Mastery

A structured, cumulative learning repository for multiphoton microscopy.

## Repository map

- [40-lesson theoretical roadmap](curriculum/roadmap.md)
- [Flashcard archive](flashcards/README.md)
- [Curated sources](references/README.md)
- [Figure archive](figures/README.md)

A cumulative, theory-only, 40-lesson curriculum covering electromagnetic optics, nonlinear excitation, ultrafast laser physics, tissue light transport, signal formation, detection, imaging-system design, and critical reading of the literature.

Future lessons will add new lesson-specific flashcards, illustrations, and source records without overwriting earlier archives. This repository is dedicated to theoretical learning, not experimental data analysis.

**Reference status:** DOI records are catalogued, but individual full-text reuse permissions have not yet been checked. No article PDFs have been archived.

## Archive integrity

Run the dependency-free validator before submitting cumulative lesson updates:

```bash
python scripts/validate_learning_archive.py
```

It checks the 40-lesson roadmap, supported flashcard schemas, globally unique card IDs, lesson-to-filename alignment, DOI catalogue structure, and local README links. GitHub Actions runs the same check for pull requests and updates to `main`.
