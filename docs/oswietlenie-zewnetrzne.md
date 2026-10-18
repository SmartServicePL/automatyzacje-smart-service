# Oświetlenie zewnętrzne

Blueprint Home Assistant do lamp przed domem i w ogrodzie: świecą od zmierzchu do ustawionej godziny albo do świtu, zapalają się przy ruchu i przy alarmie włamania. Działa bez pomocników i bez pogody.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_zewnetrzne.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_zewnetrzne_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_zewnetrzne_de.yaml)

## Ustawienia

| Pole | Klucz | Domyślnie | Opis |
|---|---|---|---|
| Lampy | `lampy` | wymagane | światła (`light`) i przełączniki oświetlenia (`switch`) na zewnątrz |
| Kiedy świeci | `kiedy_swieci` | Od zmierzchu do godziny | albo „Od zmierzchu do świtu”, albo „Tylko przy ruchu” |
| Godzina gaszenia | `godzina_gaszenia` | 23:00 | tylko przy „Od zmierzchu do godziny” |
| Czujniki ruchu | `czujniki_ruchu` | puste | czujniki `binary_sensor` na zewnątrz |
| Pełne światło po ostatnim ruchu | `czas_ruchu_min` | 3 min | 1–15 min |
| W ciszy nocnej tylko przy ruchu | `w_ciszy_tylko_ruch` | wyłączone | w ciszy nocnej lampy zgaszone, zapala je tylko ruch |
| Cisza nocna | `cisza_nocna` | puste | przełącznik `input_boolean` (włączony = noc) |
| Przy alarmie włamania zapal wszystko | `przy_alarmie_wszystko` | wyłączone | współpraca z centralą alarmu |
| Centrala alarmu | `alarm` | puste | encja `alarm_control_panel` |
| Zmierzch przy wysokości słońca | `zmierzch_elewacja` | −2° | w „Zaawansowanych”; −2° to połowa zmierzchu cywilnego |

Nazwy kluczy są stałe, bo wypełnia je też panel Smart Service.

## Jak działa

**Zmierzch i świt** liczone z położenia słońca (`sun.sun`): po zmierzchu, gdy słońce zejdzie poniżej −2°, świt, gdy znowu przekroczy −2°.

**Harmonogram.**
- „Od zmierzchu do godziny”: lampy zapalają się o zmierzchu i gasną o godzinie gaszenia. Godzina po północy (np. 01:00) znaczy gaszenie w nocy. Rano przed świtem lampy się nie zapalają.
- „Od zmierzchu do świtu”: lampy świecą całą noc.
- „Tylko przy ruchu”: lampy zapala tylko ruch.
- „W ciszy nocnej tylko przy ruchu”: na czas ciszy nocnej lampy gasną, a ruch zapala je jak w „Tylko przy ruchu”. Po końcu ciszy lampy wracają do harmonogramu (np. przy „do świtu” zimą rano znowu świecą do świtu).

Harmonogram świeci lampy bez zmiany jasności, z jasnością, którą lampa miała ostatnio.

**Ruch** działa tylko po zmierzchu, także w ciszy nocnej. Ruch zapala wszystkie lampy, lampy ze ściemnianiem na 100 %. Po ostatnim ruchu (wszystkie czujniki bez ruchu) lampy świecą jeszcze ustawiony czas, a potem wracają do stanu z harmonogramu: gasną albo świecą dalej. Ruch w dzień niczego nie zmienia. Zewnętrzne czujniki ruchu reagują też na zwierzęta i ruch gałęzi.

**Alarm.** Przy włączonym „Zapal wszystko” stan „alarm” (`triggered`) centrali zapala wszystkie lampy na 100 %, także w dzień. Gdy centrala wyjdzie ze stanu alarmu (rozbrojenie albo koniec czasu alarmu), lampy wracają do stanu z harmonogramu.

**Ręczne zmiany** zostają do najbliższego zdarzenia automatyzacji (zmierzch, świt, godzina gaszenia, cisza nocna, ruch po zmierzchu, alarm).

## Czego potrzebujesz

1. Home Assistant 2025.4 lub nowszy, z encją słońca `sun.sun` (domyślnie jest).
2. Lampy `light` albo przełączniki `switch`.

Opcjonalnie: czujniki ruchu na zewnątrz, przełącznik ciszy nocnej, centrala alarmu (np. [Smart Service Alarm](https://github.com/SmartServicePL/smartservice-alarm)).

## Ograniczenia

- Ruch, który skończył się tuż przed zmierzchem, liczy się po zmierzchu do końca ustawionego czasu.
- Po restarcie Home Assistant automatyzacja ustawia lampy według harmonogramu; ruch sprzed restartu się nie liczy.
- Wersja 1.0 nie ma osobnej jasności „tła” dla harmonogramu.

## Licencja

MIT, © 2026 Smart Service.
