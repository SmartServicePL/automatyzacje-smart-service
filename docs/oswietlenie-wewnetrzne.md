# Oświetlenie wewnętrzne

Blueprint Home Assistant, który zapala światło w pomieszczeniu, gdy czujnik wykryje obecność, a jest ciemno, i gasi je, gdy nikogo nie ma. Jedna automatyzacja obsługuje jedno pomieszczenie. Działa bez pomocników.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_wewnetrzne.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_wewnetrzne_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Foswietlenie_wewnetrzne_de.yaml)

## Ustawienia

| Pole | Klucz | Domyślnie | Opis |
|---|---|---|---|
| Czujnik obecności | `czujnik_ruchu` | wymagane | `binary_sensor` ruchu, zajętości albo obecności w pomieszczeniu |
| Lampy | `lampy` | wymagane | światła (`light`) i przełączniki oświetlenia (`switch`) |
| Tryb | `tryb` | Zapalaj i gaś | „Tylko gaś”: światło zapala człowiek, automatyzacja tylko je gasi |
| Gaś po braku obecności | `gas_po_min` | 2 min | 1–30 min, wydłuża się samo (niżej) |
| Najdłuższy czas gaszenia po powrocie | `gas_po_max_min` | 10 min | górna granica wydłużania |
| Czujnik jasności | `czujnik_lx` | puste | czujnik natężenia światła w pomieszczeniu; puste = ciemno od zachodu słońca |
| Ciemno poniżej | `prog_lx` | 10 lx | próg „ciemno” |
| Cisza nocna | `cisza_nocna` | puste | przełącznik `input_boolean` (włączony = noc); puste = bez trybu nocnego |
| Lampy nocą | `lampy_nocne` | puste | lampy zapalane w ciszy nocnej; puste = wszystkie lampy |
| Jasność nocą | `jasnosc_nocna` | 5 % | 1–100 %, tylko lampy ze ściemnianiem |
| Nocą nie zapalaj | `noca_nie_zapalaj` | wyłączone | np. sypialnia: w ciszy nocnej automatyzacja tylko gasi |
| Zapalaj tylko, gdy ktoś jest w domu | `tylko_gdy_ktos_w_domu` | wyłączone | gdy wszyscy domownicy są poza domem, światło się nie zapala |
| Domownicy | `osoby` | puste | osoby (`person`) z telefonem i lokalizacją |

Nazwy kluczy są stałe, bo wypełnia je też panel Smart Service.

## Jak działa

**Zapalanie.** Obecność w pomieszczeniu, wszystkie lampy zgaszone i ciemno: lampy się zapalają. W dzień lampy ze ściemnianiem świecą na 100 %, w ciszy nocnej tylko „Lampy nocą” na ustawionej jasności. Przełączniki (`switch`) i lampy bez ściemniania nocą świecą pełnym światłem. Gdy w pomieszczeniu świeci już jakaś lampa, automatyzacja nie dokłada innych.

**Ciemno.**
- Z czujnikiem jasności: sprawdzane tylko przy zgaszonych lampach, bo czujnik mierzy też światło lamp. Poniżej połowy progu (domyślnie poniżej 5 lx) ciemno od razu. Między połową progu a progiem ciemno dopiero po 2 minutach poniżej progu, żeby światło nie migało o zmierzchu. Gdy zmierzch przyjdzie w trakcie obecności, lampy zapalą się 2 minuty po spadku poniżej progu. Czujnik niedostępny = ciemno według słońca.
- Bez czujnika: ciemno od zachodu do wschodu słońca (`sun.sun`).
- Przy zapalonych lampach jasność nie ma znaczenia: automatyzacja nigdy nie gasi światła dlatego, że zrobiło się jasno.

**Gaszenie.** Gdy obecności nie ma przez ustawiony czas, lampy gasną. Lampy ze ściemnianiem 15 s wcześniej przygasają do połowy bieżącej jasności (najmniej 1 %), a obecność w tym czasie przywraca poprzednią jasność i odliczanie zaczyna się od nowa. Lampy świecące na 10 % albo mniej (np. nocą na 5 %) nie przygasają, tylko gasną. Przełączniki nigdy nie przygasają. Czujnik obecności niedostępny liczy się jak brak obecności.

**Czas gaszenia wydłuża się sam.** Gdy ktoś wróci najpóźniej minutę po zgaszeniu przez automatyzację, światło zapala się od razu (także gdy czujnik jasności pokazuje jeszcze światło lamp), a czas gaszenia się podwaja, najwyżej do „Najdłuższego czasu gaszenia”. Wydłużony czas obowiązuje do końca tej obecności. Czujniki często gubią osobę, która siedzi nieruchomo, i to rozwiązuje problem światła gasnącego nad głową.

**Ręczne zmiany.**
- Ręczne zgaszenie (włącznik, aplikacja, przycisk) wygrywa do końca obecności: automatyzacja nie zapala światła ponownie, dopóki pomieszczenie nie będzie puste przez ustawiony czas gaszenia.
- Ręcznie zapalone światło świeci co najmniej 30 minut od zapalenia, a potem gaśnie po zwykłym czasie bez obecności.
- Automatyzacja odróżnia własne zmiany od ręcznych po kontekście zmiany stanu lampy, bez pomocników. Zmiany z innych automatyzacji, scen i przycisków liczą się jak ręczne.

**Noc.** Cisza nocna to wspólny przełącznik domu (`input_boolean`), który włącza i wyłącza harmonogram (np. 22:00–07:00) albo przycisk „Dobranoc”. Włączenie ciszy niczego nie gasi i nie zmienia świecących lamp, zmienia tylko sposób następnego zapalenia. Na schodach warto zostawić pełne światło także nocą (puste „Lampy nocą” i jasność 100 %).

**Pusty dom.** Opcja „Zapalaj tylko, gdy ktoś jest w domu” blokuje tylko zapalanie, gdy wszyscy wybrani domownicy są poza domem. Domownik ze stanem nieznanym liczy się jako obecny. Domownicy bez telefonu w Home Assistant (np. dzieci, goście) nie zapalą wtedy światła. Opcja przydaje się, gdy w domu są zwierzęta: czujnik obecności nie odróżni kota od człowieka.

## Czego potrzebujesz

1. Home Assistant 2025.4 lub nowszy.
2. Czujnik ruchu, zajętości albo obecności w pomieszczeniu (radar mmWave albo czujka PIR).
3. Lampy `light` albo przełączniki `switch`.

Opcjonalnie: czujnik natężenia światła w pomieszczeniu (często wbudowany w czujnik obecności), przełącznik ciszy nocnej, domownicy (`person`).

## Ograniczenia

- Czujnik obecności nie odróżni zwierzęcia od człowieka. Pomaga montaż (wysokość, kąt) i ustawienia stref w czujniku.
- Zapisanie zmian w automatyzacji albo restart Home Assistant przerywa bieżącą obecność: zapamiętane ręczne zgaszenie i wydłużony czas przepadają. Świecące lampy automatyzacja przejmuje po starcie i gasi po zwykłym czasie bez obecności (lampy zapalone ręcznie w aplikacji: najwcześniej 30 minut od zapalenia).
- Ten sam czujnik w dwóch automatyzacjach zapali światło w obu pomieszczeniach.

## Licencja

MIT, © 2026 Smart Service.
