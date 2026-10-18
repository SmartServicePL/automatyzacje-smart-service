"""Stable inputs and fixed rules of the indoor and outdoor lighting blueprints."""

from __future__ import annotations

import datetime
import json
import re
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
WEWN_KEYS = {
    "czujnik_ruchu", "lampy", "tryb", "gas_po_min", "gas_po_max_min", "czujnik_lx", "prog_lx",
    "lampy_nocne", "jasnosc_nocna", "noca_nie_zapalaj", "cisza_nocna", "tylko_gdy_ktos_w_domu", "osoby",
}
WEWN_DEFAULTS = {
    "tryb": "zapalaj_i_gas", "gas_po_min": 2, "gas_po_max_min": 10, "czujnik_lx": "", "prog_lx": 10,
    "lampy_nocne": [], "jasnosc_nocna": 5, "noca_nie_zapalaj": False, "cisza_nocna": "",
    "tylko_gdy_ktos_w_domu": False, "osoby": [],
}
ZEWN_KEYS = {
    "lampy", "kiedy_swieci", "godzina_gaszenia", "zmierzch_elewacja", "czujniki_ruchu", "czas_ruchu_min",
    "w_ciszy_tylko_ruch", "cisza_nocna", "alarm", "przy_alarmie_wszystko",
}
ZEWN_DEFAULTS = {
    "kiedy_swieci": "do_godziny", "godzina_gaszenia": "23:00:00", "zmierzch_elewacja": -2, "czujniki_ruchu": [],
    "czas_ruchu_min": 3, "w_ciszy_tylko_ruch": False, "cisza_nocna": "", "alarm": "", "przy_alarmie_wszystko": False,
}
FIRST_PERSON = r"\b(zapalam|gaszę|czekam|włączam|wyłączam|przygaszam|przywracam|sprawdzam|pilnuję)\b"


def load(name: str, suffix: str = ""):
    return blueprint_i18n.load_yaml((FOLDER / f"{name}{suffix}.yaml").read_text(encoding="utf-8"))


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


def variables_with(blueprint, key: str) -> dict:
    """The first variables block (in actions) that defines ``key``."""
    for node in walk(blueprint["actions"]):
        if isinstance(node, dict) and isinstance(node.get("variables"), dict) and key in node["variables"]:
            return node["variables"]
    raise KeyError(key)


class _State:
    def __init__(self, state, last_changed=0.0, attributes=None):
        self.state = state
        self.last_changed = datetime.datetime.fromtimestamp(last_changed)
        self.attributes = attributes or {}


class _States(dict):
    """``states[entity]`` and ``states.domain.object`` like in Home Assistant templates."""

    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, domain):
        return _Domain({k.split(".", 1)[1]: v for k, v in self.items() if k.startswith(domain + ".")})


class _Domain(dict):
    def __getattr__(self, name):
        return self.get(name)


def render(template: str, states: dict | None = None, now: datetime.datetime | None = None, **variables):
    """Render a blueprint template with the few Home Assistant helpers it uses."""
    table = _States(states or {})
    moment = now or datetime.datetime(2026, 10, 18, 20, 0)

    def is_state(entity, value):
        s = table.get(entity)
        values = value if isinstance(value, list) else [value]
        return s is not None and s.state in values

    def state_attr(entity, attribute):
        s = table.get(entity)
        return None if s is None else s.attributes.get(attribute)

    env = Environment()
    env.globals.update(is_state=is_state, state_attr=state_attr, states=table, now=lambda: moment)
    env.filters["is_state"] = is_state
    env.tests["is_state"] = is_state
    env.tests["match"] = lambda value, pattern: re.match(pattern, value) is not None
    return env.from_string(template).render(**variables).strip()


class IndoorLightingTests(unittest.TestCase):
    NAME = "oswietlenie_wewnetrzne"

    def setUp(self) -> None:
        self.bp = load(self.NAME)
        self.inputs = inputs(self.bp)
        self.session = variables_with(self.bp, "ciemno")

    def test_input_keys_are_stable(self) -> None:
        for suffix in SUFFIXES:
            with self.subTest(language=suffix or "pl"):
                self.assertEqual(set(inputs(load(self.NAME, suffix))), WEWN_KEYS)

    def test_defaults_and_ranges(self) -> None:
        self.assertNotIn("default", self.inputs["czujnik_ruchu"])
        self.assertNotIn("default", self.inputs["lampy"])
        for key, value in WEWN_DEFAULTS.items():
            with self.subTest(key=key):
                self.assertEqual(self.inputs[key]["default"], value)
        number = self.inputs["gas_po_min"]["selector"]["number"]
        self.assertEqual((number["min"], number["max"]), (1, 30))
        number = self.inputs["jasnosc_nocna"]["selector"]["number"]
        self.assertEqual((number["min"], number["max"]), (1, 100))
        options = [o["value"] for o in self.inputs["tryb"]["selector"]["select"]["options"]]
        self.assertEqual(options, ["zapalaj_i_gas", "tylko_gas"])

    def test_selectors(self) -> None:
        def entity(key):
            return self.inputs[key]["selector"]["entity"]

        self.assertEqual(entity("czujnik_ruchu")["filter"],
                         [{"domain": "binary_sensor", "device_class": ["motion", "occupancy", "presence"]}])
        for key in ("lampy", "lampy_nocne"):
            self.assertEqual(entity(key)["filter"], [{"domain": ["light", "switch"]}])
            self.assertTrue(entity(key)["multiple"])
        self.assertEqual(entity("czujnik_lx")["filter"], [{"domain": "sensor", "device_class": "illuminance"}])
        self.assertEqual(entity("cisza_nocna")["filter"], [{"domain": "input_boolean"}])
        self.assertEqual(entity("osoby")["filter"], [{"domain": "person"}])

    def test_fixed_rules(self) -> None:
        variables = self.bp["variables"]
        self.assertEqual(variables["przygaszanie_s"], 15)
        self.assertEqual(variables["powrot_s"], 60)
        self.assertEqual(variables["zwloka_ciemno_s"], 120)
        self.assertEqual(variables["reczne_min_s"], 1800)
        self.assertEqual(variables["prog_przygaszania_proc"], 10)
        self.assertEqual(self.bp["mode"], "single")
        self.assertEqual(self.bp["max_exceeded"], "silent")

    def test_no_helpers_and_no_weather(self) -> None:
        text = (FOLDER / f"{self.NAME}.yaml").read_text(encoding="utf-8")
        actions = [n["action"] for n in walk(self.bp["actions"]) if isinstance(n, dict) and "action" in n]
        self.assertEqual(set(actions), {"light.turn_on", "light.turn_off", "switch.turn_on", "switch.turn_off"})
        self.assertNotRegex(text, r"weather\.|get_forecasts|domain: weather")
        self.assertIn("context.id", text)
        self.assertIn("last_changed", text)

    def test_every_wait_has_a_timeout_and_the_loop_a_limit(self) -> None:
        waits = [n for n in walk(self.bp["actions"]) if isinstance(n, dict) and ("wait_for_trigger" in n or "wait_template" in n)]
        self.assertGreaterEqual(len(waits), 6)
        for wait in waits:
            self.assertIn("timeout", wait)
        loop = next(n for n in walk(self.bp["actions"]) if isinstance(n, dict) and "repeat" in n and "until" in n["repeat"])
        self.assertIn("limit_petli", json.dumps(loop["repeat"]["until"]))

    def test_switch_never_dims(self) -> None:
        """Brightness is only sent to light entities that report a dimming colour mode."""
        for node in walk(self.bp["actions"]):
            if isinstance(node, dict) and node.get("action") == "light.turn_on" and node.get("data"):
                self.assertTrue({"brightness", "brightness_pct"} & set(node["data"]))
        dim = variables_with(self.bp, "przygaszone")
        text = json.dumps(self.bp["actions"], ensure_ascii=False)
        self.assertIn("supported_color_modes", text)
        self.assertIn("startswith('light.')", text)
        self.assertNotIn("switch.turn_on", json.dumps(dim))

    def _dark(self, **kw) -> str:
        base = dict(wlaczone=[], zgaszone_ts=0, teraz=1000.0, powrot_s=60, trigger={"id": "ruch"}, repeat={"first": True},
                    lx=None, prog_lx=10, ponizej_od=0, zwloka_ciemno_s=120)
        base.update(kw)
        states = {"sun.sun": _State(kw.pop("sun", "above_horizon"))}
        base.pop("sun", None)
        return render(self.session["ciemno"], states, **base)

    def test_darkness_rules(self) -> None:
        self.assertEqual(self._dark(wlaczone=["light.a"], lx=0.0), "nie_dotyczy")
        self.assertEqual(self._dark(lx=50.0), "jasno")
        self.assertEqual(self._dark(lx=3.0, ponizej_od=999.0), "ciemno")
        self.assertEqual(self._dark(lx=7.0, ponizej_od=970.0), "czekaj")
        self.assertEqual(self._dark(lx=7.0, ponizej_od=850.0), "ciemno")
        self.assertEqual(self._dark(lx=50.0, zgaszone_ts=980.0), "ciemno")
        self.assertEqual(self._dark(lx=7.0, ponizej_od=999.0, trigger={"id": "ciemno"}), "ciemno")
        self.assertEqual(self._dark(sun="below_horizon"), "ciemno")
        self.assertEqual(self._dark(sun="above_horizon"), "jasno")

    def _may_switch_on(self, people=None, **kw) -> bool:
        base = dict(tryb="zapalaj_i_gas", ruch_jest=True, wlaczone=[], reczne_zgaszenie=False, ktos_w_domu=True,
                    noc=False, noca_nie_zapalaj=False)
        base.update(kw)
        return render(self.session["moze_zapalic"], **base) == "True"

    def test_switch_on_rules(self) -> None:
        self.assertTrue(self._may_switch_on())
        self.assertFalse(self._may_switch_on(tryb="tylko_gas"))
        self.assertFalse(self._may_switch_on(reczne_zgaszenie=True))
        self.assertFalse(self._may_switch_on(noc=True, noca_nie_zapalaj=True))
        self.assertTrue(self._may_switch_on(noc=True))
        self.assertFalse(self._may_switch_on(ktos_w_domu=False))
        self.assertFalse(self._may_switch_on(wlaczone=["switch.a"]))

    def test_someone_at_home(self) -> None:
        template = self.session["ktos_w_domu"]

        def home(*people, enabled=True):
            states = {f"person.p{i}": _State(s) for i, s in enumerate(people)}
            return render(template, states, tylko_gdy_ktos_w_domu=enabled, osoby=list(states)) == "True"

        self.assertTrue(home("not_home", enabled=False))
        self.assertFalse(home("not_home", "Praca"))
        self.assertTrue(home("not_home", "home"))
        self.assertTrue(home("unknown"))
        self.assertTrue(render(template, {}, tylko_gdy_ktos_w_domu=True, osoby=[]) == "True")

    def test_night_lamps(self) -> None:
        template = variables_with(self.bp, "do_zapalenia")["do_zapalenia"]
        self.assertEqual(render(template, noc=True, lampy=["light.a", "switch.b"], lampy_nocne=[]), "['light.a', 'switch.b']")
        self.assertEqual(render(template, noc=True, lampy=["light.a", "switch.b"], lampy_nocne=["light.a"]), "['light.a']")
        self.assertEqual(render(template, noc=False, lampy=["light.a", "switch.b"], lampy_nocne=["light.a"]), "['light.a', 'switch.b']")

    def test_impersonal_texts(self) -> None:
        text = (FOLDER / f"{self.NAME}.yaml").read_text(encoding="utf-8").lower()
        self.assertEqual(re.findall(FIRST_PERSON, text), [])


class OutdoorLightingTests(unittest.TestCase):
    NAME = "oswietlenie_zewnetrzne"

    def setUp(self) -> None:
        self.bp = load(self.NAME)
        self.inputs = inputs(self.bp)
        self.state = variables_with(self.bp, "harmonogram")

    def test_input_keys_are_stable(self) -> None:
        for suffix in SUFFIXES:
            with self.subTest(language=suffix or "pl"):
                self.assertEqual(set(inputs(load(self.NAME, suffix))), ZEWN_KEYS)

    def test_defaults_and_selectors(self) -> None:
        self.assertNotIn("default", self.inputs["lampy"])
        for key, value in ZEWN_DEFAULTS.items():
            with self.subTest(key=key):
                self.assertEqual(self.inputs[key]["default"], value)
        options = [o["value"] for o in self.inputs["kiedy_swieci"]["selector"]["select"]["options"]]
        self.assertEqual(options, ["do_godziny", "do_switu", "tylko_ruch"])
        number = self.inputs["czas_ruchu_min"]["selector"]["number"]
        self.assertEqual((number["min"], number["max"]), (1, 15))
        self.assertEqual(self.inputs["lampy"]["selector"]["entity"]["filter"], [{"domain": ["light", "switch"]}])
        self.assertEqual(self.inputs["alarm"]["selector"]["entity"]["filter"], [{"domain": "alarm_control_panel"}])
        self.assertEqual(self.inputs["cisza_nocna"]["selector"]["entity"]["filter"], [{"domain": "input_boolean"}])
        self.assertIn("time", self.inputs["godzina_gaszenia"]["selector"])

    def test_mode_and_no_weather(self) -> None:
        self.assertEqual(self.bp["mode"], "restart")
        text = (FOLDER / f"{self.NAME}.yaml").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"weather\.|get_forecasts|domain: weather")
        condition = self.bp["conditions"][0]["value_template"]
        self.assertIn("po_zmierzchu", condition)
        self.assertIn("'ruch'", condition)

    def _window(self, hour: int, minute: int, off: str) -> bool:
        moment = datetime.datetime(2026, 10, 18, hour, minute)
        return render(self.state["w_oknie"], now=moment, godzina_gaszenia=off) == "True"

    def test_switch_off_time_window(self) -> None:
        self.assertTrue(self._window(17, 30, "23:00:00"))
        self.assertFalse(self._window(23, 0, "23:00:00"))
        self.assertFalse(self._window(5, 30, "23:00:00"))
        self.assertTrue(self._window(0, 30, "01:00:00"))
        self.assertTrue(self._window(20, 0, "01:00:00"))
        self.assertFalse(self._window(2, 0, "01:00:00"))
        self.assertFalse(self._window(6, 0, "01:00:00"))

    def _schedule(self, kiedy="do_godziny", ciemno=True, noc=False, w_ciszy=False, w_oknie=True) -> bool:
        return render(self.state["harmonogram"], kiedy_swieci=kiedy, ciemno=ciemno, noc=noc,
                      w_ciszy_tylko_ruch=w_ciszy, w_oknie=w_oknie) == "True"

    def test_schedule(self) -> None:
        self.assertTrue(self._schedule())
        self.assertFalse(self._schedule(w_oknie=False))
        self.assertFalse(self._schedule(ciemno=False))
        self.assertTrue(self._schedule(kiedy="do_switu", w_oknie=False))
        self.assertFalse(self._schedule(kiedy="tylko_ruch"))
        self.assertFalse(self._schedule(kiedy="do_switu", noc=True, w_ciszy=True))
        self.assertTrue(self._schedule(kiedy="do_switu", noc=True, w_ciszy=False))

    def _full(self, **kw) -> bool:
        base = dict(alarm_trwa=False, ciemno=True, ruch_trwa=False, ruch_pozostalo_s=0)
        base.update(kw)
        return render(self.state["pelne"], **base) == "True"

    def test_full_light_on_motion_after_dusk_and_alarm(self) -> None:
        self.assertTrue(self._full(ruch_trwa=True))
        self.assertTrue(self._full(ruch_pozostalo_s=30))
        self.assertFalse(self._full(ruch_trwa=True, ciemno=False))
        self.assertTrue(self._full(alarm_trwa=True, ciemno=False))
        self.assertFalse(self._full())
        alarm = self.state["alarm_trwa"]
        states = {"alarm_control_panel.a": _State("triggered")}
        self.assertEqual(render(alarm, states, przy_alarmie_wszystko=True, alarm="alarm_control_panel.a"), "True")
        self.assertEqual(render(alarm, states, przy_alarmie_wszystko=False, alarm="alarm_control_panel.a"), "False")
        self.assertEqual(render(alarm, states, przy_alarmie_wszystko=True, alarm=""), "False")

    def test_full_light_is_100_percent(self) -> None:
        full = next(n for n in walk(self.bp["actions"]) if isinstance(n, dict) and n.get("alias", "").startswith("Ruch po zmierzchu"))
        calls = [n for n in walk(full) if isinstance(n, dict) and n.get("action") == "light.turn_on" and n.get("data")]
        self.assertEqual([c["data"] for c in calls], [{"brightness_pct": 100}])

    def test_impersonal_texts(self) -> None:
        text = (FOLDER / f"{self.NAME}.yaml").read_text(encoding="utf-8").lower()
        self.assertEqual(re.findall(FIRST_PERSON, text), [])


class CatalogTests(unittest.TestCase):
    def test_catalog_entries(self) -> None:
        catalog = json.loads((ROOT / "katalog.json").read_text(encoding="utf-8"))
        items = {item["id"]: item for item in catalog["pozycje"]}
        for item_id, name in (("oswietlenie-wewnetrzne", "oswietlenie_wewnetrzne"), ("oswietlenie-zewnetrzne", "oswietlenie_zewnetrzne")):
            with self.subTest(item=item_id):
                item = items[item_id]
                self.assertEqual(item["wersja"], "1.0.0")
                self.assertEqual(item["licencja"], "MIT")
                self.assertEqual(item["zrzut"], "")
                self.assertEqual(item["ikona"], "https://raw.githubusercontent.com/SmartServicePL/automatyzacje-smart-service/main/assets/ikony/"
                                 f"{name}.png")
                self.assertTrue((ROOT / "assets" / "ikony" / f"{name}.png").exists())
                self.assertTrue(item["blueprint_url"].endswith(f"/{name}.yaml"))
                self.assertIn(f"{name}.yaml", item["import_url"])


if __name__ == "__main__":
    unittest.main()
