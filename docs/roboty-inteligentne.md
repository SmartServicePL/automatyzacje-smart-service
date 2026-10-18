# Inteligentny robot sprzątający – każda marka

Blueprint Home Assistant, który uruchamia robota wtedy, gdy w domu jest brudno, a nie według sztywnego harmonogramu. Pilnuje go w trakcie pracy i przy każdej decyzji zapisuje jej powód. Działa z każdą integracją, która udostępnia encję `vacuum`, także z robotami Matter.

[![Importuj do Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_inteligentne.yaml)

Wersja angielska i niemiecka: **English** [![Import to Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_inteligentne_en.yaml) **Deutsch** [![In Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_inteligentne_de.yaml)

Jedna automatyzacja steruje jednym robotem. Dwa piętra albo dwa roboty to dwie automatyzacje, każda z własnymi pomocnikami. Prostszy wariant, który sprząta tylko pod nieobecność, to [Robot sprzątający pod nieobecność](roboty-sprzatajace.md).

## Licznik brudu

Licznik rośnie, a pełne sprzątanie go zeruje. Domyślnie:

| Zdarzenie | Punkty |
|---|---|
| każda godzina (np. zwierzęta w domu) | 1 |
| każda godzina, gdy ktoś jest w domu (7–22) | 3 |
| otwarcie wybranych drzwi zewnętrznych | 2, a po deszczu 4 |
| użycie kuwety (licznik użyć) | 1 |

Deszcz („mokro”) sprawdzany jest w tej kolejności:
1. **Źródło główne** (opcjonalne): opad z ostatnich 24 h (co najmniej 1 mm) albo czujnik „pada teraz”.
2. **Zapas**: sensor opadu z 24 h, a bez niego deszcz teraz według encji pogody.

Gdy źródło główne jest podane, ale niedostępne, powód decyzji mówi „prognoza zapasowa”. Gdy nie ma ani źródła głównego, ani zapasu, automatyzacja liczy ostrożnie, jak po deszczu, i pisze to w powodzie. Zamiast licznika brudu można podać własny licznik potrzeby.

## Kiedy robot startuje

| Reguła | Warunek | Próg brudu |
|---|---|---|
| Pusty dom | wybrane dni (domyślnie pn–pt), okno 08:15–13:30, wszyscy domownicy poza domem od 10 min | 60% progu |
| Próg brudu | zwykłe okno (domyślnie 12:00–18:00) | 100% progu |
| Maksymalna przerwa | minęła maksymalna przerwa od ostatniego pełnego sprzątania (domyślnie 48 h), w jednym z okien | bez progu |

Robot nigdy nie startuje:
- w ciszy nocnej (wybrany przełącznik albo harmonogram);
- przy baterii poniżej minimum;
- gdy nie stoi w stacji;
- częściej niż „Nie częściej niż co” (domyślnie 12 h);
- wcześniej niż 3 h po nieudanej albo przerwanej próbie;
- przy włączonej blokadzie.

## Nadzór

- **Koniec sprzątania** liczy się dopiero po powrocie do stacji. Robot musi stać w stacji co najmniej 10 min, więc krótkie mycie mopów w trakcie pracy nie kończy sprzątania.
- **Pełne sprzątanie:**
  - trwa od startu co najmniej 10 min;
  - robot posprzątał co najmniej 70% swojej typowej powierzchni (mediana z 5 ostatnich pełnych sprzątań). Warunek działa, gdy podasz sensor powierzchni.

  Krótsze sprzątanie jest „Przerwane”, licznik brudu zostaje, a automatyzacja ponawia start po 3 h.
- **Pauza bez kodu błędu:** automatyzacja sama wznawia robota (najwyżej 2 razy, w godzinach 8–21, nie w ciszy nocnej).
- **Pauza z kodem błędu albo problem stacji:** tylko powiadomienie, bo zwykle potrzebny jest człowiek (np. brak wody).
- **Limit czasu** (domyślnie 5 h) liczony jest od startu. Po nim robot wraca do stacji.
- **Nie wystartował:** robot w ciągu 5 min nie ruszył albo od razu stanął z błędem. Wtedy powiadomienie i ponowienie po 3 h.
- **Ktoś wrócił** do pustego domu w trakcie sprzątania: robot wraca do stacji i dokończy później (albo staje, jeśli to obsługuje, albo sprząta dalej).
- **Sprzątanie uruchomione ręcznie** (w aplikacji albo na robocie) jest rozpoznawane. Pełne sprzątanie zeruje licznik brudu, a niepełne nie wywołuje powiadomień.
- **Kuweta** (opcjonalnie): po ustawionej liczbie użyć robot szybko sprząta wybrany obszar, w godzinach 9–21. Gdy w trakcie robot zgłosi usterkę, sprzątanie liczy się jako przerwane: licznik użyć zostaje, a kolejna próba będzie najwcześniej po godzinie.

## Powód decyzji

Każda decyzja trafia do pomocnika tekstowego, np.:
- „Czekam: brud 48/100, pusty dom od 08:15”,
- „Sprząta (pusty dom) od 08:20”,
- „Zakończono 17.10 09:05 (35 min, 31 m²)”,
- „Pauza: 210030: brak wody”,
- „Nie wystartował 08:20 (stan: paused, …)”.

Wynik sprzątania zostaje widoczny przez godzinę, potem wraca „Czekam: …”.

**Tryb podglądu** (domyślnie włączony): automatyzacja tylko zapisuje, co by zrobiła („Podgląd: wystartowałbym teraz…”), i nie wysyła komend do robota. Wyłącz go, gdy decyzje Ci odpowiadają.

## Czego potrzebujesz

1. Home Assistant 2024.10 lub nowszy (2026.3 dla sprzątania obszarów).
2. Encja `vacuum` robota.
3. Cztery pomocniki dla każdego robota. Wszystkie bez wartości początkowej, żeby przetrwały restart Home Assistant:
   - **Data i/lub czas** (data i godzina): najwcześniejszy następny start;
   - **Liczba** od 0 do 300: licznik brudu;
   - **Tekst** o maks. długości 255: stan automatyzacji;
   - **Tekst** o maks. długości 255: powód ostatniej decyzji.
4. Domownicy: osoby (`person`) z działającym lokalizatorem. Osoba ze stanem nieznanym dłużej niż dobę jest pomijana, więc nie blokuje sprzątania. Nie wybieraj czujników ruchu, jeśli w domu są zwierzęta.

Opcjonalnie:
- sensory baterii, błędu, alarmów stacji, posprzątanej powierzchni i czasu sprzątania (z integracji robota);
- drzwi zewnętrzne, sensor opadu z 24 h albo encja pogody, licznik użyć kuwety;
- cisza nocna i blokady.

## Co sprzątać

- **Cały dom:** pole obszarów puste, akcja `vacuum.start`.
- **Wybrane pomieszczenia:** obszary Home Assistant i akcja `vacuum.clean_area` (HA 2026.3+, segmenty mapy robota przypisane do obszarów w ustawieniach encji). Jeśli robot nie obsługuje obszarów, automatyzacja czeka i podaje powód.
- **Własne akcje startu:** np. akcja integracji producenta z listą pokoi i trybem mopowania.

`vacuum.start` i `vacuum.clean_area` używają bieżących ustawień robota (tryb, moc ssania). Wybrany tryb mopowania podasz tylko we własnych akcjach startu.

## Powiadomienia

W polu **Akcje powiadomienia** dodaj dowolną akcję, np. `notify.mobile_app_twoj_telefon`. Dostępne zmienne:
- `{{ tytul }}` i `{{ tresc }}`: tytuł i treść powiadomienia;
- `{{ tag }}`: ten sam dla jednego problemu, więc kolejne powiadomienie zastępuje poprzednie;
- `{{ typ }}`: `problem`, `przypomnienie`, `rozwiazany` albo `informacja`.

Problem (brak łączności, błąd, problem stacji, długa pauza, robot utknął) wysyła powiadomienie od razu. Dopóki trwa, przypomnienie przychodzi co 6 h, a w ciszy nocnej czeka do rana. Gdy problem minie, przychodzi informacja „problem usunięty”.

Opcjonalnie, osobnymi przełącznikami: **powiadomienie o starcie** sprzątania i **powiadomienie o zakończeniu** pełnego sprzątania (to samo kryterium co „Zakończono”). Przerwane sprzątanie i „nie wystartował” wysyłają powiadomienie zawsze.

## Ograniczenia

- Typowa powierzchnia uczy się z pełnych sprzątań. Przez pierwsze 3 sprzątania liczy się tylko czas.
- Punkty za drzwi przyznawane są przy każdym otwarciu. Gdy Home Assistant nie działa, otwarcia z tego czasu przepadają (użycia kuwety są nadrabiane z licznika).
- Kod błędu bez opisu (sama liczba) jest pokazywany jako liczba.

## Licencja

MIT, © 2026 Smart Service.
