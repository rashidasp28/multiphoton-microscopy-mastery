# Multiphoton Microscopy Mastery

A cumulative, theory-only, 40-lesson curriculum covering electromagnetic optics, fluorescence, nonlinear excitation, multiphoton instrumentation, and advanced photophysics.

## Learning archive
- [40-lesson roadmap](curriculum/roadmap.md)
- [Lesson 1: 25 flashcards](flashcards/stage-01-foundations/lesson-01-what-is-light.csv)
- [Scholarly articles and DOI catalogue](references/articles.csv)
- [Textbooks](references/books.md)
- [Reference preservation and copyright policy](references/README.md)

Future lessons will add new lesson-specific flashcards, illustrations, and source records without overwriting earlier archives. This repository is dedicated to theoretical learning, not experimental data analysis.

**Reference status:** DOI records are catalogued, but individual full-text reuse permissions have not yet been checked. No article PDFs have been archived.

## Archive integrity

Run the dependency-free validator before submitting cumulative lesson updates:

```bash
python scripts/validate_learning_archive.py
```

It checks the 40-lesson roadmap, supported flashcard schemas, globally unique card IDs, lesson-to-filename alignment, DOI catalogue structure, and local README links. GitHub Actions runs the same check for pull requests and updates to `main`.
