# Zmiany

## 2026-10-17 (2)

- **Inteligentny robot sprzątający – każda marka** 1.1.0. Istniejące wejścia bez zmian.
  - Nowe wejście **Powiadamiaj o zakończeniu pełnego sprzątania** (`powiadom_o_koncu`). „Powiadamiaj o starcie sprzątania” (`powiadom_o_starcie`) dotyczy teraz tylko startu.
  - Nowe opcjonalne źródło główne pogody: opad z ostatnich 24 h (`pogoda_opad_24h_wstecz`) i deszcz teraz (`pogoda_deszcz_teraz`). Gdy jest niedostępne, używany jest zapas (sensor opadu z 24 h, potem encja pogody), a powód decyzji mówi „prognoza zapasowa”. Bez żadnych danych automatyzacja liczy ostrożnie, jak po deszczu.

## 2026-10-17

- Nowa pozycja **Inteligentny robot sprzątający – każda marka** 1.0.0 (`roboty_inteligentne.yaml`, wersje `_en` i `_de`). Robot sprząta według licznika brudu (czas, obecność domowników, otwieranie drzwi z uwzględnieniem deszczu, kuweta), a nie według sztywnego harmonogramu. Trzy reguły startu: pusty dom przy niższym progu, zwykłe okno przy pełnym progu, maksymalna przerwa. Nigdy w ciszy nocnej, przy niskiej baterii ani częściej niż ustawiony odstęp. Pełne sprzątanie liczone po powrocie do stacji (czas od startu i typowa powierzchnia), wznawianie pauz bez kodu błędu, limit czasu od startu, „nie wystartował”, rozpoznanie sprzątania uruchomionego ręcznie, szybkie sprzątanie obszaru przy kuwecie, powiadomienia o problemach z przypomnieniami. Każda decyzja ma powód zapisany w pomocniku. Tryb podglądu bez komend do robota. Dotychczasowy blueprint **Robot sprzątający pod nieobecność** zostaje bez zmian.
- Generator tłumaczeń: nowy blueprint w `PAIRS`, klucz `nowy_powod` traktowany jako tekst.

## 2026-10-11 (3)

- **Automatyczne koszenie – każda kosiarka** i **Robot sprzątający pod nieobecność – każda marka**: wersje angielska i niemiecka (`koszenie_en.yaml`, `koszenie_de.yaml`, `roboty_sprzatajace_en.yaml`, `roboty_sprzatajace_de.yaml`). Każda ma własny adres źródła, więc „Importuj ponownie” pobiera tę samą wersję językową. Działanie bez zmian, tłumaczone są tylko teksty w formularzu, powiadomienia, powody w śladzie i komentarze.
- README i strony opisów: przyciski importu wersji EN i DE oraz krótka informacja po angielsku i niemiecku.
- Generator tłumaczeń (`tools/blueprint_i18n.py`) z katalogami tekstów w `i18n/` i test sprawdzający, że wersje EN i DE mają te same klucze, wartości, wyzwalacze i logikę szablonów co polski oryginał, są aktualne i nie zawierają polskiego tekstu. Test uruchamia się przy każdym wypchnięciu zmian.

## 2026-10-11 (2)

- Pozycja „X20 Max – powiadomienia o konserwacji” usunięta z katalogu. Blueprint jest nadal dostępny w repozytorium integracji.

## 2026-10-11

Pierwsza wersja katalogu.

- **Automatyczne koszenie – każda kosiarka** 1.0.0: start przy dobrych warunkach (bateria, deszcz i schnięcie, prognoza, temperatura, rosa, blokady), powrót do bazy przy deszczu, powiadomienia o problemach. Opcje domyślnie wyłączone: wybrane dni, okno godzin, tylko za dnia, przerwa, gdy ktoś jest w ogrodzie.
- **Robot sprzątający pod nieobecność – każda marka** 1.0.0: sprzątanie, gdy nikogo nie ma w domu, cały dom, wybrane obszary albo własne akcje startu, licznik potrzeby, limit czasu, powiadomienia o problemach. Opcje domyślnie wyłączone: wybrane dni i okno godzin.
- Katalog linkuje także istniejące blueprinty Smart Service: harmonogram koszenia Worx Vision / RTK i podlewanie ogrodu.
