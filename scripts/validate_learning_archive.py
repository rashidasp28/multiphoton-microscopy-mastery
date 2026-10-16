#!/usr/bin/env python3
"""Validate the cumulative learning archive without external dependencies."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
FLASHCARD_DIR = ROOT / "flashcards"
ROADMAP = ROOT / "curriculum" / "roadmap.md"
ARTICLE_CATALOGUE = ROOT / "references" / "articles.csv"
README = ROOT / "README.md"

LESSON_PATTERN = re.compile(r"^(\d+)\.\s+\S")
LESSON_FILE_PATTERN = re.compile(r"lesson-(\d{2})")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

CLASSIC_FIELDS = {"id", "lesson", "level", "front", "back", "status"}
SUMMARY_FIELDS = {
    "id",
    "lesson",
    "title",
    "core_concept",
    "fundamental_principle",
    "assumptions_or_caveats",
    "microscopy_relevance",
    "reference",
}
ARTICLE_FIELDS = {
    "citation",
    "title",
    "doi",
    "url",
    "curriculum_scope",
    "full_text_status",
}


def fail(message: str) -> None:
    raise ValueError(message)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            fail(f"{path.relative_to(ROOT)} has no header")
        rows = list(reader)
        return reader.fieldnames, rows


def validate_roadmap() -> int:
    lessons = [
        int(match.group(1))
        for line in ROADMAP.read_text(encoding="utf-8").splitlines()
        if (match := LESSON_PATTERN.match(line))
    ]
    expected = list(range(1, 41))
    if lessons != expected:
        fail("curriculum/roadmap.md must list lessons 1 through 40 exactly once and in order")
    return len(lessons)


def validate_flashcards() -> tuple[int, int]:
    files = sorted(FLASHCARD_DIR.rglob("*.csv"))
    if not files:
        fail("No flashcard CSV files found")

    seen_ids: dict[str, Path] = {}
    card_count = 0

    for path in files:
        fields, rows = read_csv(path)
        field_set = set(fields)
        if CLASSIC_FIELDS <= field_set:
            schema = "classic"
            required_values = {"id", "lesson", "level", "front", "back", "status"}
        elif SUMMARY_FIELDS <= field_set:
            schema = "summary"
            required_values = SUMMARY_FIELDS - {"fundamental_principle"}
        else:
            fail(f"{path.relative_to(ROOT)} does not match a supported flashcard schema")

        if not rows:
            fail(f"{path.relative_to(ROOT)} contains no cards")

        filename_match = LESSON_FILE_PATTERN.search(path.name)
        if filename_match is None:
            fail(f"{path.relative_to(ROOT)} must include lesson-NN in its filename")
        filename_lesson = filename_match.group(1)

        for row_number, row in enumerate(rows, start=2):
            missing = sorted(name for name in required_values if not (row.get(name) or "").strip())
            if missing:
                fail(
                    f"{path.relative_to(ROOT)}:{row_number} has empty required fields: "
                    + ", ".join(missing)
                )

            lesson = (row.get("lesson") or "").strip()
            if not re.fullmatch(r"\d{2}", lesson) or not 1 <= int(lesson) <= 40:
                fail(f"{path.relative_to(ROOT)}:{row_number} has invalid lesson {lesson!r}")
            if lesson != filename_lesson:
                fail(
                    f"{path.relative_to(ROOT)}:{row_number} lesson {lesson} does not match "
                    f"filename lesson {filename_lesson}"
                )

            if schema == "classic" and row["level"].strip() not in {"1", "2", "3", "4"}:
                fail(f"{path.relative_to(ROOT)}:{row_number} has invalid level {row['level']!r}")

            card_id = row["id"].strip()
            expected_prefix = f"L{lesson}-"
            if not card_id.startswith(expected_prefix):
                fail(
                    f"{path.relative_to(ROOT)}:{row_number} card ID {card_id!r} must start "
                    f"with {expected_prefix!r}"
                )
            if card_id in seen_ids:
                fail(
                    f"Duplicate card ID {card_id!r} in {seen_ids[card_id].relative_to(ROOT)} "
                    f"and {path.relative_to(ROOT)}"
                )
            seen_ids[card_id] = path
            card_count += 1

    return len(files), card_count


def validate_article_catalogue() -> int:
    fields, rows = read_csv(ARTICLE_CATALOGUE)
    if not ARTICLE_FIELDS <= set(fields):
        fail("references/articles.csv is missing required columns")
    if not rows:
        fail("references/articles.csv contains no records")

    seen_dois: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        missing = sorted(name for name in ARTICLE_FIELDS if not (row.get(name) or "").strip())
        if missing:
            fail(
                f"references/articles.csv:{row_number} has empty required fields: "
                + ", ".join(missing)
            )
        doi = row["doi"].strip().lower()
        if doi in seen_dois:
            fail(f"references/articles.csv:{row_number} duplicates DOI {doi}")
        seen_dois.add(doi)
        expected_url = f"https://doi.org/{row['doi'].strip()}"
        if row["url"].strip() != expected_url:
            fail(
                f"references/articles.csv:{row_number} URL must be the canonical DOI URL "
                f"{expected_url}"
            )
    return len(rows)


def validate_readme_links() -> int:
    checked = 0
    for target in MARKDOWN_LINK_PATTERN.findall(README.read_text(encoding="utf-8")):
        target = target.strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = unquote(target.split("#", 1)[0])
        resolved = (README.parent / relative).resolve()
        if ROOT not in resolved.parents and resolved != ROOT:
            fail(f"README.md link escapes the repository: {target}")
        if not resolved.exists():
            fail(f"README.md contains a broken local link: {target}")
        checked += 1
    return checked


def main() -> int:
    try:
        lesson_count = validate_roadmap()
        flashcard_files, card_count = validate_flashcards()
        article_count = validate_article_catalogue()
        link_count = validate_readme_links()
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Archive validation failed: {error}", file=sys.stderr)
        return 1

    print(
        "Archive validation passed: "
        f"{lesson_count} roadmap lessons, {card_count} cards in {flashcard_files} files, "
        f"{article_count} reference records, and {link_count} README links checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
