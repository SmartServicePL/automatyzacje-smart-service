# Robot sprzątający pod nieobecność – każda marka

Blueprint Home Assistant, który uruchamia robota odkurzającego lub mopującego, gdy nikogo nie ma w domu, i pilnuje go w trakcie pracy. Działa z każdą integracją, która udostępnia encję `vacuum`, np. Roborock, Ecovacs, Dreame, urządzenia Matter.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_sprzatajace.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_sprzatajace_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_sprzatajace_de.yaml)

Jedna automatyzacja steruje jednym robotem. Masz dwa piętra albo dwa roboty? Utwórz dwie automatyzacje z tego blueprintu, każdą z własnym pomocnikiem.

## Co robi

Co 10 minut sprawdza, czy można sprzątać. Robot startuje, gdy jednocześnie:

- nikogo nie ma w domu od ustawionej liczby minut (albo wybrano tryb „bez względu na obecność”),
- robot stoi w stacji z wystarczającą baterią,
- minął odstęp od ostatniego sprzątania,
- opcjonalny licznik potrzeby osiągnął próg (np. „brud” albo liczba użyć kuwety),
- żadna blokada nie jest włączona.

W trakcie sprzątania:

- gdy ktoś wróci, robot wraca do stacji i dokończy później (albo staje, albo sprząta dalej – do wyboru),
- po przekroczeniu limitu czasu robot wraca do stacji,
- błąd, długa pauza i brak łączności wysyłają jedno powiadomienie na zdarzenie.

### Opcje domyślnie wyłączone

| Opcja | Co robi po włączeniu |
|---|---|
| Sprzątać tylko w wybrane dni | Start tylko w zaznaczone dni tygodnia. |
| Sprzątać tylko w wybranych godzinach | Start tylko w oknie godzin. Okno może przechodzić przez północ. |

## Co sprzątać

Do wyboru są trzy sposoby:

1. **Cały dom** – zostaw pole obszarów puste. Automatyzacja użyje `vacuum.start`.
2. **Wybrane pomieszczenia** – wybierz obszary Home Assistant. Automatyzacja użyje akcji `vacuum.clean_area`. Wymaga Home Assistant 2026.3 lub nowszego i robota z obsługą „Sprzątaj obszar”. Segmenty mapy robota trzeba najpierw przypisać do obszarów w ustawieniach encji robota. Jeśli robot nie obsługuje obszarów, automatyzacja nie wystartuje i poda powód w śladzie (trace).
3. **Własne akcje startu** – włącz opcję i dodaj akcję integracji producenta, np. sprzątanie pokoi po ID z wybranym trybem mopowania i mocą ssania.

## Czego potrzebujesz

1. Home Assistant 2024.10 lub nowszy (2026.3 dla sprzątania obszarów).
2. Encja `vacuum` robota.
3. Pomocnik **Data i/lub czas** z datą i godziną, np. „Najwcześniejsze następne sprzątanie”. Tworzysz go w *Ustawienia → Urządzenia i usługi → Pomocnicy → Utwórz pomocnika → Data i/lub czas → Data i godzina*. Każdy robot potrzebuje własnego pomocnika.
4. Domownicy: osoby (`person`), urządzenia (`device_tracker`), grupy albo czujniki obecności. Stan nieznany liczy się jako „ktoś jest w domu”. Nie wybieraj czujników ruchu w pomieszczeniach, w których są zwierzęta.

## Jak liczony jest odstęp

- Po komendzie startu pomocnik dostaje *teraz + ponowienie* (domyślnie 3 h). Jeśli robot nie ruszy, następna próba będzie najwcześniej po tym czasie.
- Gdy robot sprząta bez przerwy przez ustawiony czas (domyślnie 15 min), sprzątanie jest uznane za wykonane i pomocnik dostaje *teraz + odstęp* (domyślnie 44 h). Liczy się też sprzątanie uruchomione ręcznie.
- Po powrocie domownika albo po limicie czasu pomocnik dostaje *teraz + ponowienie*, więc robot dokończy później.

Pole **Akcje po wykonanym sprzątaniu** służy np. do wyzerowania licznika potrzeby.

## Powiadomienia

W polu **Akcje powiadomienia** dodaj dowolną akcję, np. `notify.mobile_app_twoj_telefon`, ze zmiennymi `{{ tytul }}` i `{{ tresc }}`. Puste pole = bez powiadomień.

## Masz robota Dreame?

Właścicielom robotów Dreame polecamy też [Dreame Scheduler](https://github.com/botts7/dreame-scheduler) autorstwa botts7 (licencja MIT). To integracja z harmonogramem tygodniowym dla każdego pokoju i raportami ze sprzątania. Wymaga integracji [Dreame Vacuum](https://github.com/Tasshack/dreame-vacuum) i Home Assistant 2025.12 lub nowszego.

## Ograniczenia

- Powiadomienia o zakończeniu sprzątania są celowo pominięte. Bez danych producenta nie da się odróżnić końca pracy od doładowania w stacji w trakcie sprzątania.
- Tryb „wstrzymaj robota” po powrocie domownika nie wznawia pracy sam.

## Licencja

MIT, © 2026 Smart Service.
