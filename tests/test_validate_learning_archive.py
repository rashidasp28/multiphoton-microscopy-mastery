import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate_learning_archive.py"
SPEC = importlib.util.spec_from_file_location("validate_learning_archive", MODULE_PATH)
assert SPEC and SPEC.loader
archive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archive
SPEC.loader.exec_module(archive)


SUMMARY_FIELDS = [
    "id",
    "lesson",
    "title",
    "core_concept",
    "fundamental_principle",
    "assumptions_or_caveats",
    "microscopy_relevance",
    "reference",
]
ARTICLE_FIELDS = [
    "citation",
    "title",
    "doi",
    "url",
    "curriculum_scope",
    "full_text_status",
]


class LearningArchiveValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "curriculum").mkdir()
        (self.root / "flashcards" / "stage-01-foundations").mkdir(parents=True)
        (self.root / "references").mkdir()

        self.original_paths = (
            archive.ROOT,
            archive.FLASHCARD_DIR,
            archive.ROADMAP,
            archive.ARTICLE_CATALOGUE,
            archive.README,
        )
        archive.ROOT = self.root
        archive.FLASHCARD_DIR = self.root / "flashcards"
        archive.ROADMAP = self.root / "curriculum" / "roadmap.md"
        archive.ARTICLE_CATALOGUE = self.root / "references" / "articles.csv"
        archive.README = self.root / "README.md"

        archive.ROADMAP.write_text(
            "# Roadmap\n\n" + "\n".join(f"{number}. Lesson {number}" for number in range(1, 41)),
            encoding="utf-8",
        )
        archive.README.write_text("[Roadmap](curriculum/roadmap.md)\n", encoding="utf-8")
        self.write_flashcards(
            "lesson-01-summary.csv",
            [self.summary_card("L01-C01", "01")],
        )
        self.write_articles([self.article("10.1000/example")])

    def tearDown(self):
        (
            archive.ROOT,
            archive.FLASHCARD_DIR,
            archive.ROADMAP,
            archive.ARTICLE_CATALOGUE,
            archive.README,
        ) = self.original_paths
        self.temporary_directory.cleanup()

    def summary_card(self, card_id: str, lesson: str) -> dict[str, str]:
        return {
            "id": card_id,
            "lesson": lesson,
            "title": "Test concept",
            "core_concept": "A concise explanation",
            "fundamental_principle": "",
            "assumptions_or_caveats": "Test scope",
            "microscopy_relevance": "Test relevance",
            "reference": "Test reference",
        }

    def article(self, doi: str) -> dict[str, str]:
        return {
            "citation": "Example 2026",
            "title": "Example article",
            "doi": doi,
            "url": f"https://doi.org/{doi}",
            "curriculum_scope": "Lesson 1",
            "full_text_status": "DOI link only",
        }

    def write_flashcards(self, filename: str, rows: list[dict[str, str]]) -> None:
        path = self.root / "flashcards" / "stage-01-foundations" / filename
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def write_articles(self, rows: list[dict[str, str]]) -> None:
        with archive.ARTICLE_CATALOGUE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=ARTICLE_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_archive_passes_all_checks(self):
        self.assertEqual(archive.validate_roadmap(), 40)
        self.assertEqual(archive.validate_flashcards(), (1, 1))
        self.assertEqual(archive.validate_article_catalogue(), 1)
        self.assertEqual(archive.validate_readme_links(), 1)

    def test_duplicate_flashcard_id_is_rejected(self):
        self.write_flashcards(
            "lesson-01-extra.csv",
            [self.summary_card("L01-C01", "01")],
        )
        with self.assertRaisesRegex(ValueError, "Duplicate card ID"):
            archive.validate_flashcards()

    def test_lesson_must_match_filename(self):
        self.write_flashcards(
            "lesson-01-summary.csv",
            [self.summary_card("L02-C01", "02")],
        )
        with self.assertRaisesRegex(ValueError, "does not match filename lesson"):
            archive.validate_flashcards()

    def test_duplicate_doi_is_case_insensitive(self):
        self.write_articles(
            [self.article("10.1000/example"), self.article("10.1000/EXAMPLE")]
        )
        with self.assertRaisesRegex(ValueError, "duplicates DOI"):
            archive.validate_article_catalogue()

    def test_broken_readme_link_is_rejected(self):
        archive.README.write_text("[Missing](missing.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "broken local link"):
            archive.validate_readme_links()


if __name__ == "__main__":
    unittest.main()
