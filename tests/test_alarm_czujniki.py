"""Stable inputs and fixed rules of the alarm blueprint."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import blueprint_i18n  # noqa: E402

FOLDER = ROOT / "blueprints" / "automation" / "smart_service"
SOURCE = FOLDER / "alarm_czujniki.yaml"

# Input keys are filled by the panel, so they never change after the first release.
INPUT_KEYS = {
    "alarm", "czujniki_obwod", "czujniki_ruch", "czujniki_zagrozen", "syreny", "syrena_min",
    "cichy_alarm", "odbiorcy", "uzbrajaj_na_noc", "cisza_nocna", "przypomnij_gdy_wyszli",
    "osoby", "pomocnik_powod",
}
DEFAULTS = {
    "czujniki_obwod": [], "czujniki_ruch": [], "czujniki_zagrozen": [], "syreny": [],
    "syrena_min": 3, "cichy_alarm": False, "odbiorcy": [], "uzbrajaj_na_noc": False,
    "cisza_nocna": "", "przypomnij_gdy_wyszli": False, "osoby": [], "pomocnik_powod": "",
}
WHAT_TO_DO = {"": "Co zrobić:", "_en": "What to do:", "_de": "Was tun:"}


def load(suffix: str = ""):
    return blueprint_i18n.load_yaml((FOLDER / f"alarm_czujniki{suffix}.yaml").read_text(encoding="utf-8"))


def inputs(blueprint) -> dict:
    found = {}
    for section in blueprint["blueprint"]["input"].values():
        found.update(section["input"])
    return found


def walk(node):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


class AlarmBlueprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bp = load()
        self.inputs = inputs(self.bp)

    def test_input_keys_are_stable(self) -> None:
        self.assertEqual(set(self.inputs), INPUT_KEYS)
        for suffix in ("_en", "_de"):
            with self.subTest(language=suffix):
                self.assertEqual(set(inputs(load(suffix))), INPUT_KEYS)

    def test_defaults(self) -> None:
        self.assertNotIn("default", self.inputs["alarm"])
        for key, value in DEFAULTS.items():
            with self.subTest(key=key):
                self.assertEqual(self.inputs[key]["default"], value)
        number = self.inputs["syrena_min"]["selector"]["number"]
        self.assertEqual((number["min"], number["max"]), (1, 10))

    def test_selectors(self) -> None:
        def entity_filter(key):
            return self.inputs[key]["selector"]["entity"]["filter"]

        self.assertEqual(entity_filter("alarm"), [{"domain": "alarm_control_panel"}])
        self.assertEqual(entity_filter("cisza_nocna"), [{"domain": "input_boolean"}])
        self.assertEqual(entity_filter("pomocnik_powod"), [{"domain": "input_text"}])
        self.assertEqual(entity_filter("osoby"), [{"domain": "person"}])
        self.assertEqual(entity_filter("syreny"), [{"domain": "siren"}])
        classes = {
            "czujniki_obwod": ["door", "window", "opening", "garage_door"],
            "czujniki_ruch": ["motion", "occupancy", "presence"],
            "czujniki_zagrozen": ["smoke", "carbon_monoxide", "gas", "moisture"],
        }
        for key, expected in classes.items():
            with self.subTest(key=key):
                self.assertEqual(entity_filter(key), [{"domain": "binary_sensor", "device_class": expected}])
                self.assertTrue(self.inputs[key]["selector"]["entity"]["multiple"])
        device = self.inputs["odbiorcy"]["selector"]["device"]
        self.assertTrue(device["multiple"])
        self.assertEqual(device["filter"], [{"integration": "mobile_app"}])

    def test_fixed_rules(self) -> None:
        variables = self.bp["variables"]
        self.assertEqual(self.bp["mode"], "parallel")
        self.assertEqual(variables["prog_baterii"], 15)
        self.assertEqual(variables["powtorzenia"], 5)
        self.assertEqual(variables["odstep_powtorzen_s"], 120)
        self.assertEqual(self.bp["blueprint"]["homeassistant"]["min_version"], "2026.7.0")

    def _step(self, alias: str) -> dict:
        return next(step for step in self.bp["actions"] if step["alias"].startswith(alias))

    def test_disarm_only_after_quiet_night(self) -> None:
        """No notification action can disarm: alarm_disarm sits only in the two end-of-night steps."""
        owners = []
        for step in self.bp["actions"]:
            if any(isinstance(n, dict) and n.get("action") == "alarm_control_panel.alarm_disarm" for n in walk(step)):
                owners.append(json.dumps(step["if"], ensure_ascii=False))
        self.assertEqual(len(owners), 2)
        self.assertIn("noc_koniec", owners[1])
        self.assertIn("smart_service", owners[1])
        self.assertIn("not smart_service", owners[0])
        for condition in owners:
            self.assertNotIn("uzbroj", condition)
            self.assertNotIn("przyjalem", condition)

    def test_other_panel_remembers_the_night(self) -> None:
        """Other panels: pending or triggered during the night, or a restart, means no disarm in the morning."""
        step = self._step("Obca centrala")
        text = json.dumps(step, ensure_ascii=False)
        self.assertIn("noc_start", text)
        self.assertIn("trigger.id == 'start'", text)
        then = step["then"]
        wait = next(s for s in then if "wait_template" in s)
        self.assertIn("is_state(cisza_nocna, 'off')", wait["wait_template"])
        self.assertIn("not in ['arming', 'armed_night']", wait["wait_template"])
        self.assertFalse(wait["continue_on_timeout"])
        flag = next(s for s in then if "variables" in s and "noc_alarm" in s["variables"])
        self.assertIn("['pending', 'triggered']", flag["variables"]["noc_alarm"])
        choose = next(s for s in then if "choose" in s)["choose"]
        refuse, disarm = choose
        self.assertIn("noc_alarm", refuse["conditions"][0]["value_template"])
        self.assertIn("po_restarcie", refuse["conditions"][0]["value_template"])
        self.assertFalse(any(isinstance(n, dict) and n.get("action", "").endswith("alarm_disarm") for n in walk(refuse)))
        guard = disarm["conditions"][0]["value_template"]
        self.assertIn("not po_restarcie", guard)
        self.assertIn("is_state(alarm, 'armed_night')", guard)
        # The old rule (armed_night at most 15 minutes after the start of quiet night) is gone.
        self.assertNotIn("900", text)

    def test_daily_check_skipped_in_quiet_night(self) -> None:
        condition = self._step("Codzienny przegląd")["if"][0]["value_template"]
        self.assertIn("is_state(cisza_nocna, 'on')", condition)
        self.assertFalse(any(isinstance(n, dict) and "wait_template" in n for n in walk(self._step("Codzienny przegląd"))))

    def test_impersonal_texts(self) -> None:
        texts = self.bp["variables"]["teksty"]
        self.assertTrue(texts["przyjete_tresc"].startswith("Potwierdzenie: {imie}"))
        self.assertTrue(texts["uzbrojony_tresc"].startswith("Uzbrojenie: {imie}"))
        joined = " ".join(texts.values())
        self.assertNotIn("Potwierdził", joined)
        self.assertNotIn("Uzbroił:", joined)

    def test_notification_texts_end_with_what_to_do(self) -> None:
        kinds = ("smoke", "carbon_monoxide", "gas", "moisture")
        for suffix, prefix in WHAT_TO_DO.items():
            texts = load(suffix)["variables"]["teksty"]
            with self.subTest(language=suffix or "pl"):
                bodies = [key for key in texts if "_tresc" in key]
                self.assertEqual(len(bodies), 16)
                for key in bodies:
                    lines = texts[key].split("\n")
                    self.assertEqual(len(lines), 2, key)
                    self.assertTrue(lines[1].startswith(prefix + " "), key)
                    self.assertTrue(lines[1][len(prefix) + 1].isupper(), key)
                for kind in kinds:
                    self.assertIn(f"zagrozenie_{kind}", texts)
                    self.assertIn(f"zagrozenie_tresc_{kind}", texts)
                self.assertFalse([key for key in texts if key.endswith("_inne")])

    def test_approved_texts(self) -> None:
        """Samples of the texts approved on 17.10.2026 (A1-A16), word for word."""
        texts = self.bp["variables"]["teksty"]
        approved = {
            "wlamanie_tytul": "Alarm: włamanie",
            "zagrozenie_tresc_moisture": "Czujnik {czujnik} wykrył wodę o {godzina}.\nCo zrobić: Zakręć główny zawór wody i sprawdź miejsce przy czujniku.",
            "noc_odmowa_tytul": "Alarm nieuzbrojony na noc",
            "rano_odmowa_tytul": "Alarm nadal uzbrojony",
            "rano_restart_tresc": "Alarm nie został rozbrojony, bo w nocy był restart systemu.\nCo zrobić: Rozbrój alarm ręcznie przed otwarciem drzwi.",
            "uzbroj_odmowa_tytul": "Alarm nieuzbrojony",
            "czujniki_tresc": "{lista}.\nCo zrobić: Sprawdź zasilanie i zasięg czujnika albo wymień baterię.",
        }
        for key, text in approved.items():
            with self.subTest(key=key):
                self.assertEqual(texts[key], text)

    def test_no_first_person(self) -> None:
        """Texts and step names are impersonal: no "uzbroiłem", "rozbrajam" and similar forms."""
        text = SOURCE.read_text(encoding="utf-8").lower()
        forms = r"\b(uzbroiłem|rozbroiłem|wyzwoliłem|uzbrajam|rozbrajam|czekam|ruszam|wysyłam|wyłączam|włączam)\b"
        self.assertEqual(re.findall(forms, text), [])
        self.assertNotIn("home assistant", " ".join(self.bp["variables"]["teksty"].values()).lower())

    def test_critical_notifications(self) -> None:
        found = [n for n in walk(self.bp["actions"]) if isinstance(n, dict) and "interruption-level" in n.get("push", {})]
        self.assertEqual(len(found), 2)
        for data in found:
            self.assertEqual(data["priority"], "high")
            self.assertEqual(data["ttl"], 0)
            self.assertEqual(data["channel"], "{{ teksty.kanal }}")
            self.assertEqual(data["push"]["interruption-level"], "critical")
            self.assertEqual(data["push"]["sound"]["critical"], 1)
        self.assertEqual(self.bp["variables"]["teksty"]["kanal"], "awarie")


if __name__ == "__main__":
    unittest.main()
