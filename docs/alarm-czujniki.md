# Alarm – czujniki i tryb nocny

Blueprint Home Assistant, który łączy czujniki domu z centralą alarmu i wysyła powiadomienia krytyczne na telefony. Działa z centralą [Smart Service Alarm](https://github.com/SmartServicePL/smartservice-alarm) i z każdą inną centralą `alarm_control_panel`.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Falarm_czujniki.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Falarm_czujniki_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Falarm_czujniki_de.yaml)

Jedna automatyzacja obsługuje jedną centralę.

## Czujniki

| Lista | Rodzaje czujników | Kiedy działa |
|---|---|---|
| Drzwi i okna (obwód) | drzwi, okno, otwarcie, brama garażowa | uzbrojenie poza domem, w domu i na noc |
| Ruch i obecność | ruch, zajętość, obecność | tylko uzbrojenie poza domem (w domu są ludzie i zwierzęta) |
| Zagrożenia | dym, czad, gaz, zalanie | zawsze, także przy rozbrojonym alarmie i w ciszy nocnej |

Uzbrojenie „wakacje” (`armed_vacation`) obcej centrali działa jak „poza domem”.

**Włamanie.** Czujnik z listy właściwej dla trybu zmienia stan na „włączony”, a automatyzacja wyzwala centralę: Smart Service Alarm akcją `smartservice_alarm.trigger` z nazwą czujnika, inną centralę akcją `alarm_control_panel.alarm_trigger`. Opóźnienie wejścia i czas trwania alarmu ustawiasz w centrali. Centrala, która nie obsługuje wyzwolenia, dostaje tylko powiadomienia i syreny z automatyzacji.

**Zagrożenie.** Syreny i powiadomienie krytyczne bez zmiany stanu centrali. Tytuł, treść i „Co zrobić” zależą od rodzaju czujnika: dym, czad, gaz albo zalanie (np. „Alarm: dym”, „Czujnik Kuchnia wykrył dym o 23:14.”).

## Powiadomienia krytyczne

Gdy centrala przejdzie w stan „alarm” albo czujnik wykryje zagrożenie, wybrane telefony dostają powiadomienie krytyczne:
- Android: kanał „awarie”, priorytet wysoki, `ttl: 0`. Żeby przebijało tryb „Nie przeszkadzać”, w ustawieniach kanału „awarie” w telefonie włącz zastępowanie trybu „Nie przeszkadzać”.
- iOS: dźwięk krytyczny (przebija wyciszenie i „Nie przeszkadzać”).

Powiadomienie ma przycisk **PRZYJĄŁEM** i wraca co 2 minuty, najwyżej 5 razy. Pierwsze naciśnięcie PRZYJĄŁEM na dowolnym telefonie:
- gasi powiadomienie na wszystkich telefonach,
- wysyła wszystkim „Potwierdzenie: imię” (osoba przypisana do konta Home Assistant, z którego przyszło naciśnięcie),
- przy zagrożeniu wyłącza syreny.

Włamanie przestaje się powtarzać także po rozbrojeniu albo po końcu alarmu w centrali.

**Telefony** (`odbiorcy`): urządzenia z aplikacją Home Assistant. Puste pole = wszystkie telefony z aplikacją. Automatyzacja wysyła do akcji `notify.mobile_app_<nazwa urządzenia>`, gdzie nazwa to nazwa nadana przez aplikację przy rejestracji. Zmiana nazwy urządzenia w Home Assistant tego nie psuje, ale nowa rejestracja aplikacji pod inną nazwą tak: wtedy wybierz telefon ponownie.

## Syreny

- Włamanie: syreny działają przez ustawiony czas (domyślnie 3 min). **Cichy alarm** = włamanie bez syren, tylko powiadomienia.
- Zagrożenie: syreny zawsze, także przy cichym alarmie. Gasną po PRZYJĄŁEM, po rozbrojeniu albo gdy czujnik wrócił do „wyłączony” i minął ustawiony czas.
- Rozbrojenie zawsze wyłącza wszystkie syreny, także przed końcem czasu.
- Po starcie Home Assistant syreny są wyłączane, jeśli centrala nie jest w stanie „alarm” i żaden czujnik zagrożeń nie wykrywa zagrożenia.

## Noc (opcjonalnie)

**Uzbrajaj na noc według ciszy nocnej.** Wymaga przełącznika ciszy nocnej (`input_boolean`, harmonogram ustawia panel albo Ty).
- Początek ciszy nocnej: uzbrojenie na noc bez kodu, tylko gdy alarm jest rozbrojony. Uzbrojonego alarmu („poza domem”, „w domu”) ani trwającego alarmu automatyzacja nie rusza.
- Koniec ciszy nocnej: rozbrojenie bez kodu, tylko gdy to uzbrojenie na noc zrobiła automatyzacja i od tego czasu nie było alarmu. Uzbrojenia ręcznego nie rusza.
- Był alarm w nocy: rano bez rozbrojenia, powiadomienie „Alarm nadal uzbrojony” z treścią „Alarm nie został rozbrojony, bo w nocy był alarm.”.
- Odmowa centrali (np. otwarte okno z listy czujników sprawdzanych przy uzbrojeniu) = powiadomienie „Alarm nieuzbrojony na noc” z powodem, np. „Zamknij: Okno salon”.
- Centrala wymagająca kodu do uzbrojenia: automatyzacja jej nie uzbraja i podaje powód. Kodu nie zapisuje się w automatyzacji.

Z centralą Smart Service Alarm rozbrojenie po nocy działa dzięki jej zasadzie: automatyzacja może rozbroić bez PIN-u tylko uzbrojenie na noc zrobione przez automatyzację, bez alarmu od tego czasu. Dodaj czujniki drzwi i okien do „Czujników sprawdzanych przy uzbrojeniu” w ustawieniach centrali, żeby otwarte okno blokowało uzbrojenie.

**Inna centrala** (nie Smart Service Alarm) nie mówi, kto ją uzbroił ani czy w nocy był alarm, więc automatyzacja pamięta noc sama:
- uzbrajanie na noc działa tylko z centralą bez kodu (`code_format` puste), bo inaczej rano nie dałoby się jej rozbroić;
- od uzbrojenia na początku ciszy nocnej automatyzacja pilnuje centrali do rana. Rano rozbraja ją tylko wtedy, gdy przez całą noc była w stanie „uzbrajanie” albo „uzbrojony na noc”;
- przejście w „oczekiwanie” (`pending`) albo „alarm” (`triggered`) w nocy, także krótkie, z powrotem do „uzbrojony na noc”: rano bez rozbrojenia i powiadomienie „Alarm nie został rozbrojony, bo w nocy był alarm.”;
- rozbrojenie albo inne uzbrojenie w nocy przez użytkownika kończy pilnowanie: rano automatyzacja niczego nie zmienia;
- restart Home Assistant w nocy: pamięć nocy przepada, więc rano bez rozbrojenia i powiadomienie „Alarm nie został rozbrojony, bo w nocy był restart systemu.”.

## Wyjście z domu (opcjonalnie)

**Przypomnij, gdy wszyscy wyszli.** Gdy wszyscy wybrani domownicy (`person`) są poza domem od 2 minut, a alarm jest rozbrojony, przychodzi powiadomienie „Wszyscy wyszli, alarm nieuzbrojony”. Domownik ze stanem nieznanym krócej niż dobę liczy się jako obecny.
- Centrala bez kodu do uzbrojenia: przycisk **Uzbrój** uzbraja „poza domem” i wysyła wszystkim „Uzbrojenie: imię”. Odmowa centrali przychodzi jako powiadomienie z powodem.
- Centrala z kodem do uzbrojenia: przycisk **Otwórz alarm** otwiera okno alarmu w aplikacji (Android; iOS otwiera aplikację).

Z powiadomienia nie da się rozbroić alarmu.

## Pilnowanie czujników

Dla wszystkich czujników z trzech list:
- brak łączności (stan „niedostępny”) dłużej niż 30 minut: powiadomienie „Czujnik alarmu nie działa”; w ciszy nocnej czeka do jej końca;
- codziennie o 9:00 przegląd: czujniki bez łączności od ponad doby i baterie poniżej 15% (czujnik baterii tego samego urządzenia, `device_class: battery`, także czujnik „słaba bateria”). Jedno powiadomienie na dzień, dopóki problem trwa. Gdy o 9:00 trwa cisza nocna, tego dnia przegląd nic nie wysyła.

## Powód decyzji (opcjonalnie)

Pomocnik **Tekst** (maks. 255 znaków) dostaje ostatnią decyzję, np.:
- „Uzbrojony na noc o 22:00”,
- „Nieuzbrojony na noc: Zamknij: Okno salon”,
- „Wyzwolenie alarmu: Drzwi wejściowe o 23:14”,
- „Potwierdzenie: Anna o 23:15”,
- „Nie rozbrojony po nocy: w nocy był alarm”.

## Teksty powiadomień

Wszystkie teksty są na początku sekcji `variables` w mapie `teksty` (tytuł, 1–2 zdania, w nowej linii „Co zrobić: …”), bezosobowo, w brzmieniu zatwierdzonym 17.10.2026. W miejsce `{czujnik}`, `{godzina}`, `{imie}`, `{powod}`, `{lista}`, `{godzin}` i `{procent}` automatyzacja wstawia wartości.

## Czego potrzebujesz

1. Home Assistant 2026.7 lub nowszy.
2. Centrala alarmu: [Smart Service Alarm](https://github.com/SmartServicePL/smartservice-alarm) albo dowolna encja `alarm_control_panel`.
3. Czujniki `binary_sensor` z odpowiednią klasą urządzenia.
4. Do powiadomień: aplikacja Home Assistant na telefonach.

Opcjonalnie: syreny (`siren`), przełącznik ciszy nocnej (`input_boolean`), domownicy (`person`) i pomocnik Tekst na powód decyzji.

## Ograniczenia

- Gdy Home Assistant nie działa, nikt nie wyzwala centrali ani nie wysyła powiadomień. Restart przerywa powtarzanie powiadomienia i czekanie na koniec ciszy nocnej z powiadomieniem o czujniku.
- Inna centrala: zapisanie zmian w tej automatyzacji w nocy też kasuje pamięć nocy. Rano centrala zostaje wtedy uzbrojona na noc, bez powiadomienia.
- Czujnik, który był niedostępny już przed restartem, pojawi się w przeglądzie dopiero po dobie od restartu (licznik czasu zaczyna się od nowa).
- „Potwierdzenie” pokazuje imię osoby przypisanej do konta Home Assistant z aplikacji. Konto bez osoby = „ktoś z domowników”.
- Uzbrojenie na noc innej automatyzacji centrala Smart Service Alarm traktuje tak samo jak uzbrojenie z tego blueprintu.
- Czujnik zagrożeń, któremu później zmieniono klasę urządzenia na inną niż dym, czad, gaz albo zalanie, dostaje teksty dymu (najbezpieczniejsze zalecenie).

## Licencja

MIT, © 2026 Smart Service.
