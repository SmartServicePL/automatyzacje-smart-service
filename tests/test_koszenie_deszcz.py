"""Rain sources, quiet night and reason helper of the lawn mowing blueprint."""

from __future__ import annotations

import datetime
import json
import sys
import unittest
from pathlib import Path

from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import blueprint_i18n  # noqa: E402

FOLDER = ROOT / "blueprints" / "automation" / "smart_service"
SUFFIXES = ("", "_en", "_de")

# Input keys are filled by the panel, so they never change after the first release.
EXISTING_KEYS = {
    "kosiarka", "bateria", "min_bateria", "pomocnik_nastepne", "ogranicz_dni", "dni", "ogranicz_godziny", "okno_od",
    "okno_do", "odstep_godz", "ponowienie_godz", "min_czas_koszenia_min", "czujniki_deszczu", "schniecie_godz",
    "prognoza", "prognoza_godz", "max_opad_mm", "max_prawdopodobienstwo", "temperatura", "min_temp", "max_temp",
    "wilgotnosc", "min_roznica_rosy", "tylko_za_dnia", "slonce_min", "sprawdzaj_ogrod", "czujniki_ogrodu",
    "reakcja_ogrod", "blokady", "deszcz_do_bazy", "pauza_alarm_min", "max_czas_koszenia_godz", "powiadom_o_starcie",
    "akcje_powiadomien",
}
NEW_KEYS = {"pogoda_opad_24h_wstecz", "deszcz_24h", "cisza_nocna", "pomocnik_powod"}


def load(suffix: str = ""):
    return blueprint_i18n.load_yaml((FOLDER / f"koszenie{suffix}.yaml").read_text(encoding="utf-8"))


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


class _State:
    def __init__(self, state, last_changed=0.0, attributes=None):
        self.state = state
        self.last_changed = datetime.datetime.fromtimestamp(last_changed)
        self.attributes = attributes or {}


class _States(dict):
    """``states(entity)`` and ``states[entity]`` like in Home Assistant templates."""

    def __call__(self, entity):
        s = self.get(entity)
        return "unknown" if s is None else s.state

    def __getitem__(self, key):
        return self.get(key)


NOW = datetime.datetime(2026, 10, 19, 11, 0)


def _is_number(value) -> bool:
    try:
        float(value)
    except (TypeError, ValueError):
        return False
    return True


def evaluate(bp, values: dict, states: dict) -> dict:
    """Evaluate the blueprint ``variables`` in order, like Home Assistant does."""
    table = _States(states)

    def is_state(entity, value):
        s = table.get(entity)
        values_ = value if isinstance(value, list) else [value]
        return s is not None and s.state in values_

    def state_attr(entity, attribute):
        s = table.get(entity)
        return None if s is None else s.attributes.get(attribute)

    def today_at(text):
        hour, minute, *_ = (int(x) for x in text.split(":"))
        return NOW.replace(hour=hour, minute=minute, second=0)

    env = Environment()
    env.globals.update(is_state=is_state, state_attr=state_attr, states=table, now=lambda: NOW, today_at=today_at)
    env.filters["is_number"] = _is_number
    env.filters["timestamp_custom"] = lambda ts, fmt="%Y", local=True: datetime.datetime.fromtimestamp(ts).strftime(fmt)
    context: dict = {}
    for key, value in bp["variables"].items():
        if isinstance(value, dict) and "!input" in value:
            name = value["!input"]
            context[key] = values.get(name, inputs(bp)[name].get("default"))
        elif isinstance(value, str) and ("{{" in value or "{%" in value):
            context[key] = env.from_string(value).render(**context).strip()
        else:
            context[key] = value
    context["__env__"] = env
    return context


def render(context: dict, template: str, **extra) -> str:
    env = context["__env__"]
    return env.from_string(template).render(**{**context, **extra}).strip()


def variables_with(bp, key: str) -> dict:
    for node in walk(bp["actions"]):
        if isinstance(node, dict) and isinstance(node.get("variables"), dict) and key in node["variables"]:
            return node["variables"]
    raise KeyError(key)


BASE_INPUTS = {
    "kosiarka": "lawn_mower.m", "bateria": "", "min_bateria": 60, "pomocnik_nastepne": "input_datetime.n",
    "czujniki_deszczu": [], "temperatura": "", "wilgotnosc": "", "prognoza": "", "blokady": [],
    "czujniki_ogrodu": [], "pomocnik_powod": "input_text.powod",
}
DOCKED = {"lawn_mower.m": _State("docked"), "input_datetime.n": _State("2026-10-01 00:00:00")}


class RainSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bp = load()

    def source(self, main="", reserve="", states=None) -> str:
        values = dict(BASE_INPUTS, pogoda_opad_24h_wstecz=main, deszcz_24h=reserve)
        return evaluate(self.bp, values, dict(DOCKED, **(states or {})))["zrodlo_pogody"]

    def blocked(self, main="", reserve="", quiet="", states=None) -> str:
        values = dict(BASE_INPUTS, pogoda_opad_24h_wstecz=main, deszcz_24h=reserve, cisza_nocna=quiet)
        return evaluate(self.bp, values, dict(DOCKED, **(states or {})))["powod_blokady"]

    def test_input_keys_are_stable(self) -> None:
        for suffix in SUFFIXES:
            with self.subTest(language=suffix or "pl"):
                self.assertEqual(set(inputs(load(suffix))), EXISTING_KEYS | NEW_KEYS)

    def test_new_inputs_are_optional_entities(self) -> None:
        found = inputs(self.bp)
        for key in NEW_KEYS:
            with self.subTest(key=key):
                self.assertEqual(found[key]["default"], "")
        domains = {key: [f["domain"] for f in found[key]["selector"]["entity"]["filter"]] for key in NEW_KEYS}
        self.assertEqual(domains["pogoda_opad_24h_wstecz"], ["sensor"])
        self.assertEqual(domains["deszcz_24h"], ["sensor"])
        self.assertEqual(domains["pomocnik_powod"], ["input_text"])
        self.assertIn("input_boolean", domains["cisza_nocna"])

    def test_main_source_has_priority(self) -> None:
        states = {"sensor.main": _State("0.2"), "sensor.local": _State("9")}
        self.assertEqual(self.source("sensor.main", "sensor.local", states), "glowne")
        self.assertEqual(self.blocked("sensor.main", "sensor.local", states=states), "")

    def test_reserve_when_main_is_unavailable(self) -> None:
        for broken in ("unavailable", "unknown"):
            with self.subTest(main=broken):
                states = {"sensor.main": _State(broken), "sensor.local": _State("5.5")}
                self.assertEqual(self.source("sensor.main", "sensor.local", states), "rezerwa")
                self.assertIn("5.5 mm", self.blocked("sensor.main", "sensor.local", states=states))
        states = {"sensor.main": _State("unavailable"), "sensor.local": _State("0")}
        self.assertEqual(self.blocked("sensor.main", "sensor.local", states=states), "")

    def test_only_local_sensor_is_not_a_fallback(self) -> None:
        states = {"sensor.local": _State("0.4")}
        self.assertEqual(self.source("", "sensor.local", states), "zapas")

    def test_unknown_weather_blocks_the_start(self) -> None:
        states = {"sensor.main": _State("unavailable"), "sensor.local": _State("unknown")}
        self.assertEqual(self.source("sensor.main", "sensor.local", states), "nieznane")
        self.assertIn("pogoda nieznana", self.blocked("sensor.main", "sensor.local", states=states))
        self.assertIn("pogoda nieznana", self.blocked("sensor.missing", states={}))
        self.assertIn("pogoda nieznana", self.blocked("", "sensor.missing", states={}))

    def test_no_rain_sensor_keeps_the_old_behaviour(self) -> None:
        self.assertEqual(self.source(), "brak")
        self.assertEqual(self.blocked(), "")

    def test_wet_grass_threshold_is_one_millimetre(self) -> None:
        self.assertEqual(self.blocked("sensor.main", states={"sensor.main": _State("0.9")}), "")
        self.assertIn("mm deszczu", self.blocked("sensor.main", states={"sensor.main": _State("1.0")}))

    def test_quiet_night(self) -> None:
        on = {"input_boolean.cisza": _State("on")}
        off = {"input_boolean.cisza": _State("off")}
        self.assertEqual(self.blocked(quiet="input_boolean.cisza", states=on), "cisza nocna")
        self.assertEqual(self.blocked(quiet="input_boolean.cisza", states=off), "")
        self.assertEqual(self.blocked(quiet="", states=on), "")

    def test_quiet_night_does_not_hide_a_mower_that_is_away(self) -> None:
        states = {"input_boolean.cisza": _State("on"), "lawn_mower.m": _State("mowing")}
        self.assertIn("nie stoi w bazie", self.blocked(quiet="input_boolean.cisza", states=states))


class ReasonHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bp = load()
        self.blocked_branch = next(
            n for n in walk(self.bp["actions"])
            if isinstance(n, dict) and n.get("alias") == "Zapisz powód, dla którego kosiarka nie wyjeżdża"
        )

    def reason(self, main="", reserve="", states=None, **extra) -> str:
        values = dict(BASE_INPUTS, pogoda_opad_24h_wstecz=main, deszcz_24h=reserve, cisza_nocna="")
        context = evaluate(self.bp, values, dict(DOCKED, **(states or {})))
        template = self.blocked_branch["sequence"][0]["variables"]["nowy_powod"]
        return render(context, template, **extra)

    def test_fallback_is_written(self) -> None:
        states = {"sensor.main": _State("unavailable"), "sensor.local": _State("3")}
        text = self.reason("sensor.main", "sensor.local", states)
        self.assertTrue(text.startswith("Nie koszę - "), text)
        self.assertTrue(text.endswith("(pogoda zapasowa)"), text)

    def test_unknown_weather_is_written(self) -> None:
        states = {"sensor.main": _State("unavailable"), "sensor.local": _State("unavailable")}
        text = self.reason("sensor.main", "sensor.local", states)
        self.assertIn("pogoda nieznana", text)
        self.assertTrue(text.endswith("(pogoda nieznana)"), text)

    def test_main_source_adds_no_note(self) -> None:
        text = self.reason("sensor.main", states={"sensor.main": _State("2.4")})
        self.assertNotIn("(pogoda", text)

    def test_branch_runs_for_fallback_even_when_the_mower_is_away(self) -> None:
        condition = self.blocked_branch["conditions"][1]["value_template"]
        self.assertIn("zrodlo_pogody in ['rezerwa', 'nieznane']", condition)
        states = {"sensor.main": _State("unavailable"), "sensor.local": _State("2"), "lawn_mower.m": _State("mowing")}
        text = self.reason("sensor.main", "sensor.local", states)
        self.assertTrue(text.startswith("Kosiarka poza bazą"), text)
        self.assertTrue(text.endswith("(pogoda zapasowa)"), text)

    def test_every_write_is_guarded_and_cut_to_255_characters(self) -> None:
        writes = [n for n in walk(self.bp["actions"]) if isinstance(n, dict) and n.get("action") == "input_text.set_value"]
        self.assertGreaterEqual(len(writes), 4)
        for write in writes:
            self.assertEqual(write["target"]["entity_id"], "{{ pomocnik_powod }}")
            self.assertTrue(write["data"]["value"].endswith("[:255] }}"))
        guarded = [
            n for n in walk(self.bp["actions"])
            if isinstance(n, dict) and "if" in n and "pomocnik_powod != ''" in json.dumps(n["if"])
            and "input_text.set_value" in json.dumps(n["then"])
        ]
        self.assertEqual(len(guarded), len(writes))

    def test_reason_texts_are_impersonal_except_the_agreed_mowing_line(self) -> None:
        text = (FOLDER / "koszenie.yaml").read_text(encoding="utf-8")
        for forbidden in ("Nie mogę", "Czekam", "Sprawdzam", "Uważam"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
