import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
SPEC = importlib.util.spec_from_file_location("brain_validate", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class BundleFixture:
    def __init__(self):
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.parent = Path(self._temporary_directory.name)
        self.root = self.parent / "brain"
        self.root.mkdir()

    def close(self):
        self._temporary_directory.cleanup()

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def concept(self, relative_path="concept.md", body="Body", extra_frontmatter=""):
        return self.write(
            relative_path,
            "---\n"
            "type: Reference\n"
            f"{extra_frontmatter}"
            "---\n"
            f"# Concept\n\n{body}\n",
        )

    def index(self, relative_path="index.md", links="[Concept](concept.md)"):
        return self.write(relative_path, f"# Index\n\n{links}\n")


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.fixture = BundleFixture()

    def tearDown(self):
        self.fixture.close()

    def diagnostics(self, report, severity=None):
        items = report.diagnostics
        if severity:
            items = [item for item in items if item.severity == severity]
        return {item.code for item in items}

    def make_valid_bundle(self):
        self.fixture.concept()
        self.fixture.index()

    def test_valid_bundle_has_no_findings(self):
        self.make_valid_bundle()

        report = validator.validate(self.fixture.root)

        self.assertEqual(report.concept_count, 1)
        self.assertEqual(report.diagnostics, [])
        self.assertEqual(report.exit_status, 0)

    def test_unknown_types_and_producer_fields_are_accepted(self):
        self.fixture.write(
            "concept.md",
            """---
type: Bespoke Domain Object
producer:
  nested: true
producer.extension: enabled
"quoted producer key": accepted
tags:
  - one
  - two
---
# Concept
""",
        )
        self.fixture.index()

        report = validator.validate(self.fixture.root)

        self.assertEqual(report.diagnostics, [])

    def test_quoted_type_key_is_accepted(self):
        self.fixture.write("concept.md", '---\n"type": Reference\n---\n# Concept\n')
        self.fixture.index()

        report = validator.validate(self.fixture.root)

        self.assertEqual(report.diagnostics, [])

    def test_missing_frontmatter_is_an_error(self):
        self.fixture.write("concept.md", "# Concept\n")
        self.fixture.index()

        report = validator.validate(self.fixture.root)

        self.assertIn("FRONTMATTER_MISSING", self.diagnostics(report, validator.ERROR))
        self.assertEqual(report.exit_status, 1)

    def test_unclosed_frontmatter_is_an_error(self):
        self.fixture.write("concept.md", "---\ntype: Reference\n")

        report = validator.validate(self.fixture.root)

        self.assertIn("FRONTMATTER_UNCLOSED", self.diagnostics(report, validator.ERROR))

    def test_missing_empty_and_non_string_type_are_errors(self):
        examples = {
            "missing.md": "---\ntitle: Missing\n---\n",
            "empty.md": "---\ntype:\n---\n",
            "list.md": "---\ntype: [one, two]\n---\n",
            "boolean.md": "---\ntype: true\n---\n",
            "number.md": "---\ntype: 42\n---\n",
        }
        for path, content in examples.items():
            self.fixture.write(path, content)

        report = validator.validate(self.fixture.root)

        self.assertEqual(len(report.errors), 5)
        self.assertIn("TYPE_MISSING", self.diagnostics(report, validator.ERROR))
        self.assertIn("TYPE_INVALID", self.diagnostics(report, validator.ERROR))

    def test_duplicate_type_is_an_error(self):
        self.fixture.write(
            "concept.md",
            "---\ntype: Reference\ntype: Other\n---\n",
        )

        report = validator.validate(self.fixture.root)

        self.assertIn("TYPE_DUPLICATE", self.diagnostics(report, validator.ERROR))

    def test_malformed_top_level_yaml_is_an_error(self):
        self.fixture.write(
            "concept.md",
            "---\ntype: Reference\nthis is not a mapping\n---\n",
        )

        report = validator.validate(self.fixture.root)

        self.assertIn("FRONTMATTER_MALFORMED", self.diagnostics(report, validator.ERROR))

    def test_invalid_utf8_is_an_error(self):
        self.fixture.write("concept.md", b"---\ntype: Reference\n---\n\xff")

        report = validator.validate(self.fixture.root)

        self.assertIn("READ_FAILED", self.diagnostics(report, validator.ERROR))

    def test_broken_internal_link_is_a_warning_and_does_not_fail(self):
        self.fixture.concept(body="See [Missing](missing.md).")
        self.fixture.index()

        report = validator.validate(self.fixture.root)

        self.assertIn("LINK_BROKEN", self.diagnostics(report, validator.WARNING))
        self.assertEqual(report.errors, [])
        self.assertEqual(report.exit_status, 0)

    def test_balanced_parentheses_in_internal_link_are_supported(self):
        self.fixture.concept("target_(one).md")
        self.fixture.concept(
            "source.md",
            body="See [Target](target_(one).md).",
        )
        self.fixture.index(links="[Target](target_(one).md)\n[Source](source.md)")

        report = validator.validate(self.fixture.root)

        self.assertNotIn("LINK_BROKEN", self.diagnostics(report))

    def test_external_citations_are_outside_validation(self):
        self.fixture.concept(
            "section/concept.md",
            body=(
                "[Web](https://example.com/source) "
                "[File](../../outside.md) "
                "[Absolute](/outside.md)"
            ),
        )
        self.fixture.index("section/index.md", "[Concept](concept.md)")
        self.fixture.index(links="[Section](section/)")

        report = validator.validate(self.fixture.root)

        self.assertNotIn("LINK_BROKEN", self.diagnostics(report))

    def test_missing_index_coverage_is_a_warning(self):
        self.fixture.concept()

        report = validator.validate(self.fixture.root)

        self.assertIn("INDEX_MISSING", self.diagnostics(report, validator.WARNING))
        self.assertEqual(report.exit_status, 0)

    def test_existing_index_must_link_each_concept(self):
        self.fixture.concept()
        self.fixture.index(links="Nothing yet.")

        report = validator.validate(self.fixture.root)

        self.assertIn("INDEX_ENTRY_MISSING", self.diagnostics(report, validator.WARNING))

    def test_subdirectory_index_must_be_linked_from_parent_index(self):
        self.fixture.concept("section/concept.md")
        self.fixture.index("section/index.md", "[Concept](concept.md)")
        self.fixture.index(links="Nothing yet.")

        report = validator.validate(self.fixture.root)

        self.assertIn("INDEX_ENTRY_MISSING", self.diagnostics(report, validator.WARNING))

    def test_valid_change_log_conventions_have_no_warning(self):
        self.make_valid_bundle()
        self.fixture.write(
            "log.md",
            "# Change Log\n\n## 2026-07-14\n\n**Recorded** a concept.\n\n"
            "## 2026-07-13\n\n**Revised** a concept.\n",
        )

        report = validator.validate(self.fixture.root)

        self.assertFalse(any(code.startswith("LOG_") for code in self.diagnostics(report)))

    def test_change_log_heading_dates_and_order_are_warnings(self):
        self.make_valid_bundle()
        self.fixture.write(
            "log.md",
            "# Updates\n\n## 2026-07-13\n\nFirst.\n\n## 2026-07-14\n\nSecond.\n",
        )

        report = validator.validate(self.fixture.root)

        codes = self.diagnostics(report, validator.WARNING)
        self.assertIn("LOG_HEADING", codes)
        self.assertIn("LOG_ORDER", codes)

    def test_empty_change_log_warns_without_failing(self):
        self.make_valid_bundle()
        self.fixture.write("log.md", "")

        report = validator.validate(self.fixture.root)

        codes = self.diagnostics(report, validator.WARNING)
        self.assertIn("LOG_HEADING", codes)
        self.assertIn("LOG_DATES_MISSING", codes)
        self.assertEqual(report.exit_status, 0)

    def test_only_recognized_tool_metadata_directories_are_skipped(self):
        self.make_valid_bundle()
        self.fixture.write(".git/bad.md", "not a concept")
        self.fixture.write(".obsidian/bad.md", "not a concept")
        self.fixture.write("scratch/bad.md", "not a concept")

        report = validator.validate(self.fixture.root)

        self.assertEqual(report.concept_count, 2)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0].path, "scratch/bad.md")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_symlinked_external_content_is_not_traversed(self):
        outside = self.fixture.parent / "outside.md"
        outside.write_text("not a concept", encoding="utf-8")
        os.symlink(str(outside), str(self.fixture.root / "external.md"))
        self.make_valid_bundle()

        report = validator.validate(self.fixture.root)

        self.assertEqual(report.concept_count, 1)
        self.assertEqual(report.errors, [])

    def test_invalid_root_and_usage_fail(self):
        output = io.StringIO()
        status = validator.main([], output)
        self.assertEqual(status, 1)
        self.assertIn("Usage:", output.getvalue())

        missing_output = io.StringIO()
        status = validator.main([str(self.fixture.root / "missing")], missing_output)
        self.assertEqual(status, 1)
        self.assertIn("ROOT_INVALID", missing_output.getvalue())

    def test_human_report_keeps_warnings_and_errors_separate(self):
        self.fixture.write("bad.md", "not a concept")
        self.fixture.concept("orphan.md")

        report = validator.validate(self.fixture.root)
        rendered = validator.render_report(report)

        self.assertIn("Warnings (", rendered)
        self.assertIn("Errors (", rendered)
        self.assertIn("[WARN]", rendered)
        self.assertIn("[FAIL]", rendered)
        self.assertTrue(rendered.endswith("Validation FAILED.\n"))


if __name__ == "__main__":
    unittest.main()
