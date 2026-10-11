# Automatyczne koszenie – każda kosiarka

Blueprint Home Assistant, który uruchamia robota koszącego wtedy, gdy warunki są dobre, i pilnuje go w trakcie pracy. Działa z każdą integracją, która udostępnia encję `lawn_mower`, np. Husqvarna Automower, Worx Landroid, Segway Navimow, Gardena smart, Mammotion, Ecovacs GOAT.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Fkoszenie.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Fkoszenie_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Fkoszenie_de.yaml)

Masz kosiarkę Worx Vision / RTK? Zobacz też [inteligentny harmonogram Worx](https://github.com/SmartServicePL/worx_vision_cloud_plus_automation). Liczy przyrost trawy i wybiera godzinę z prognozy.

## Co robi

Co 10 minut sprawdza, czy można kosić. Kosiarka startuje, gdy jednocześnie:

- stoi w bazie i ma co najmniej ustawiony poziom baterii,
- minął odstęp od ostatniego koszenia,
- nie pada, a od końca deszczu minął czas schnięcia trawy (gdy wybrano czujnik deszczu),
- prognoza godzinowa nie przewiduje deszczu w najbliższych godzinach (gdy wybrano prognozę),
- temperatura mieści się w zakresie i na trawie nie ma rosy (gdy wybrano czujniki),
- żadna blokada nie jest włączona.

W trakcie koszenia:

- deszcz odsyła kosiarkę do bazy,
- błąd, długa pauza, brak łączności i zbyt długie koszenie wysyłają jedno powiadomienie na zdarzenie.

### Opcje domyślnie wyłączone

| Opcja | Co robi po włączeniu |
|---|---|
| Kosić tylko w wybrane dni | Start tylko w zaznaczone dni tygodnia. |
| Kosić tylko w wybranych godzinach | Start tylko w oknie godzin. Okno może przechodzić przez północ, np. 22:00–05:00. |
| Kosić tylko za dnia | Start tylko, gdy słońce jest co najmniej X° nad horyzontem (encja `sun.sun`). Zalecane: jeże i inne małe zwierzęta żerują po zmroku. |
| Nie kosić, gdy ktoś jest w ogrodzie | Brak startu, gdy któryś czujnik ma stan „on”. Gdy ktoś wejdzie podczas koszenia, kosiarka wraca do bazy albo staje na trawniku. |

Bez tych opcji kosiarka może wystartować o każdej porze doby.

## Czego potrzebujesz

1. Home Assistant 2024.10 lub nowszy.
2. Encja `lawn_mower` kosiarki.
3. Pomocnik **Data i/lub czas** z datą i godziną, np. „Najwcześniejsze następne koszenie”. Tworzysz go w *Ustawienia → Urządzenia i usługi → Pomocnicy → Utwórz pomocnika → Data i/lub czas → Data i godzina*. Automatyzacja sama zapisuje w nim, kiedy najwcześniej wolno kosić. Każda kosiarka potrzebuje własnego pomocnika.
4. Wyłączony harmonogram w aplikacji producenta. Inaczej kosiarka będzie kosiła także sama.

Opcjonalnie: sensor baterii, czujnik deszczu (`binary_sensor`), encja `weather` z prognozą godzinową, czujniki temperatury i wilgotności, czujniki „ktoś w ogrodzie”, przełączniki blokady.

## Jak liczony jest odstęp

- Po komendzie startu automatyzacja ustawia pomocnik na *teraz + ponowienie* (domyślnie 2 h). Jeśli kosiarka nie wyjedzie, następna próba będzie najwcześniej po tym czasie. Nie ma pętli startów ani lawiny powiadomień.
- Gdy kosiarka kosi bez przerwy przez ustawiony czas (domyślnie 20 min), koszenie jest uznane za wykonane i pomocnik dostaje *teraz + odstęp* (domyślnie 44 h). Liczy się też koszenie uruchomione ręcznie albo z aplikacji.

## Powiadomienia

W polu **Akcje powiadomienia** dodaj dowolną akcję, np. `notify.mobile_app_twoj_telefon`. W treści możesz użyć zmiennych `{{ tytul }}` i `{{ tresc }}`:

```yaml
action: notify.mobile_app_twoj_telefon
data:
  title: "{{ tytul }}"
  message: "{{ tresc }}"
```

Puste pole = bez powiadomień. Opcja „Powiadamiaj także o starcie…” dodaje powiadomienia o starcie i o zatrzymaniu przez deszcz lub ogród.

## Ograniczenia

- Czas schnięcia liczy się od ostatniej zmiany czujnika deszczu na „off”. Restart Home Assistant, który odświeży czujnik, może wydłużyć schnięcie.
- Tryb „zatrzymaj na trawniku” (ogród) nie wznawia koszenia sam. Wznów kosiarkę ręcznie albo odeślij ją do bazy.
- Prognoza musi mieć dane godzinowe. Bez nich, gdy nie wybrano czujnika deszczu, kosiarka nie wystartuje. Dzięki temu nie ruszy w ciemno przed deszczem.

## Licencja

MIT, © 2026 Smart Service.
