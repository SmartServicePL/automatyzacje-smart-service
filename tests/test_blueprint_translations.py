"""The English and German blueprints must match the Polish source and the catalog."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import blueprint_i18n  # noqa: E402

SOURCE_URL = (
    "https://github.com/SmartServicePL/automatyzacje-smart-service/blob/main/"
    "blueprints/automation/smart_service/"
)

SAMPLE = """\
blueprint:
  name: Harmonogram
  source_url: https://example.com/blueprints/sample.yaml
triggers:
  - trigger: time
    id: start
    at: "08:00:00"
actions:
  - alias: Zapisz termin
  - variables:
      label: >-
        {% if days == 1 %}jutro rano{% else %}{{ {0: 'dziś'}.get(days, 'później') }}{% endif %}
      code: "{{ 'docked' if x else 'mowing' }}"
      ocena: >-
        {%- if n == 0 -%}brak
        {%- else -%}ok{%- endif -%}
      powod_blokady: >-
        {%- if x -%}
          pada
        {%- endif -%}
"""


class TranslationsTests(unittest.TestCase):
    def test_generated_blueprints_match_source_and_catalog(self) -> None:
        for source, catalog in blueprint_i18n.PAIRS:
            with self.subTest(blueprint=source.name):
                problems = blueprint_i18n.check(source, catalog)
                self.assertEqual(problems, [], "\n".join(problems[:30]))

    def test_every_translation_has_its_own_source_url(self) -> None:
        for source, _ in blueprint_i18n.PAIRS:
            for lang in blueprint_i18n.LANGUAGES:
                path = blueprint_i18n.output_path(source, lang)
                with self.subTest(blueprint=path.name):
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(f"  source_url: {SOURCE_URL}{path.name}\n", text)

    def test_source_blueprints_point_to_themselves(self) -> None:
        for source, _ in blueprint_i18n.PAIRS:
            with self.subTest(blueprint=source.name):
                text = source.read_text(encoding="utf-8")
                self.assertIn(f"  source_url: {SOURCE_URL}{source.name}\n", text)


class CheckerTests(unittest.TestCase):
    """The checker itself must catch changes other than text."""

    def setUp(self) -> None:
        self.source = blueprint_i18n.load_yaml(SAMPLE)

    def _differences(self, translated: str) -> list[str]:
        return blueprint_i18n.structure_differences(self.source, blueprint_i18n.load_yaml(translated))

    def test_text_only_translation_passes(self) -> None:
        translated = (
            SAMPLE.replace("Harmonogram", "Schedule")
            .replace("Zapisz termin", "Save the time")
            .replace("jutro rano", "tomorrow morning")
            .replace("'dziś'", "'today'")
            .replace("'później'", "'later'")
            .replace("pada", "it is raining")
        )
        self.assertEqual(self._differences(translated), [])

    def test_changed_trigger_id_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("id: start", "id: begin")))

    def test_changed_template_logic_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("days == 1", "days == 2")))

    def test_changed_state_literal_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("'docked'", "'angedockt'")))

    def test_changed_code_in_template_output_fails(self) -> None:
        self.assertTrue(self._differences(SAMPLE.replace("-%}brak", "-%}none")))
        self.assertTrue(self._differences(SAMPLE.replace("-%}ok{%-", "-%}gut{%-")))

    def test_segments_skip_logic_and_codes(self) -> None:
        texts = [segment.text for segment in blueprint_i18n.segments(SAMPLE)]
        self.assertIn("Zapisz termin", texts)
        self.assertTrue(any("jutro" in text for text in texts))
        self.assertFalse(any("docked" in text for text in texts))
        self.assertFalse(any("brak" in text for text in texts))
        self.assertFalse(any(text.startswith("id:") for text in texts))

    def test_single_word_reason_is_a_segment(self) -> None:
        texts = [segment.text for segment in blueprint_i18n.segments(SAMPLE)]
        self.assertIn("pada", texts)


class CheckFilesTests(unittest.TestCase):
    """check() must report missing translations, stale files and Polish leftovers."""

    TRANSLATIONS = {
        "Harmonogram": "Schedule",
        "Zapisz termin": "Save the time",
        "{% if days == 1 %}jutro rano{% else %}{{ {0: 'dziś'}.get(days, 'później') }}{% endif %}":
            "{% if days == 1 %}tomorrow morning{% else %}{{ {0: 'today'}.get(days, 'later') }}{% endif %}",
        "pada": "raining",
    }

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        folder = Path(self.tmp.name)
        self.source = folder / "sample.yaml"
        self.catalog = folder / "catalog.yaml"
        self.source.write_text(SAMPLE, encoding="utf-8", newline="\n")
        self._save(self.TRANSLATIONS)
        self.assertEqual(self._build(), 0)

    def _build(self) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return blueprint_i18n.cmd_build(self.source, self.catalog)

    def _save(self, translations: dict[str, str]) -> None:
        entries = [{"pl": pl, "en": text, "de": text} for pl, text in translations.items()]
        blueprint_i18n.save_catalog(self.catalog, entries)

    def _problems(self) -> list[str]:
        return blueprint_i18n.check(self.source, self.catalog)

    def test_built_files_pass(self) -> None:
        self.assertEqual(self._problems(), [])

    def test_missing_translation_fails(self) -> None:
        self._save({**self.TRANSLATIONS, "pada": ""})
        self.assertTrue(any("missing translation" in p for p in self._problems()))

    def test_stale_generated_file_fails(self) -> None:
        path = blueprint_i18n.output_path(self.source, "en")
        path.write_text(path.read_text(encoding="utf-8").replace("Schedule", "Plan"), encoding="utf-8")
        self.assertTrue(any("out of date" in p for p in self._problems()))

    def test_polish_letters_left_fail(self) -> None:
        self._save({**self.TRANSLATIONS, "Zapisz termin": "Zapisz termin teraz, proszę"})
        self._build()
        self.assertTrue(any("Polish text left" in p for p in self._problems()))

    def test_unused_catalog_entry_fails(self) -> None:
        self._save({**self.TRANSLATIONS, "Stary tekst": "Old text"})
        self.assertTrue(any("stale segment" in p for p in self._problems()))


if __name__ == "__main__":
    unittest.main()
