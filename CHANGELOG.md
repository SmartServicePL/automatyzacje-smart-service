# Zmiany

## 2026-10-19

- **Automatyczne koszenie – każda kosiarka** 1.1.0. Istniejące wejścia bez zmian; nowe są opcjonalne i domyślnie puste.
  - Nowe wejścia `pogoda_opad_24h_wstecz` (źródło główne, sensor opadu z 24 godzin w mm; panel wypełnia go czujnikiem MIGIELS) i `deszcz_24h` (własny czujnik, zapas). Co najmniej 1 mm w ciągu doby = trawa mokra, brak startu. Istniejące czujniki deszczu (`czujniki_deszczu`) działają jak dotąd.
  - Pogoda nieznana: gdy podano któryś czujnik opadu z 24 godzin, a żaden nie jest dostępny, kosiarka nie wyjeżdża.
  - Nowe wejście `cisza_nocna` (przełącznik, harmonogram lub czujnik): w ciszy nocnej kosiarka nie wyjeżdża, trwające koszenie nie jest przerywane.
  - Nowe wejście `pomocnik_powod` (pomocnik Tekst, do 255 znaków): ostatnia decyzja lub powód odmowy, np. „Koszę od 11:00 - trawa sucha”, także dla odmowy z powodu prognozy. Przejście na zapas dopisuje „(pogoda zapasowa)”, nieznana pogoda „(pogoda nieznana)”; oba wpisy powstają zawsze.
  - Testy: `tests/test_koszenie_deszcz.py` (pierwszeństwo, zapas, pogoda nieznana, cisza nocna, stałość nazw wejść, teksty powodu). Wersje EN i DE przebudowane z katalogu tłumaczeń.
- **Smart mowing schedule (Worx)**: wersja 0.11.0 w repozytorium `worx_vision_cloud_plus_automation` z tymi samymi wejściami (`pogoda_opad_24h_wstecz`, `deszcz_24h`, `cisza_nocna`, `pomocnik_powod`); dotychczasowy „Zmierzony opad” zostaje ostatnim zapasem, a czujnik deszczu kosiarki bez zmian.

## 2026-10-22

- **Inteligentny robot sprzątający – każda marka** 1.2.0. Istniejące wejścia bez zmian.
  - Nowy przycisk „Usunąłem przeszkodę - kontynuuj”: przy pauzie i błędzie powiadomienie dostaje zmienne `kontynuuj`, `kontynuuj_akcja` i `kontynuuj_tekst`. Naciśnięcie wznawia sprzątanie (w trybie podglądu tylko zapis), a powód mówi, czy się udało. To samo robi zdarzenie `smart_service_robot_kontynuuj` z `entity_id` robota, np. z przycisku w panelu. Robot nie wznawia się sam.
  - Powód czekania podaje prawdziwą przyczynę: „start w oknie 12:00-18:00”, „czekam na pusty dom (domownicy w domu)”, „dziś poza dniami sprzątania”, „maksymalna przerwa minęła”; przy „najbliższy start od …” także stan brudu.
  - Pomocnik daty (najbliższy możliwy start) poza godzinami sprzątania przesuwa się na początek najbliższego okna, zamiast zostawać w przeszłości.
  - Generator tłumaczeń: klucz `kontynuuj_tekst` traktowany jako tekst.
- Ikony automatyzacji (`assets/ikony`): nowe logo Smart Service (biały domek na jasnoniebieskim kafelku) zamiast poprzedniego znaku.

## 2026-10-18

- **Inteligentny robot sprzątający – każda marka** 1.1.2. Wejścia bez zmian.
  - Kuweta: gdy robot w trakcie szybkiego sprzątania stanie z kodem błędu, po powrocie do stacji wynik to „Kuweta: przerwane - usterka”, a nie „obszar posprzątany”. Licznik użyć się nie zeruje, kolejna próba najwcześniej po godzinie.
- **Inteligentny robot sprzątający – każda marka** 1.1.1. Wejścia bez zmian.
  - Tryb podglądu: decyzja o sprzątaniu przy kuwecie jest zapisywana raz (z godziną) i licznik kuwety się zeruje, tak jak po prawdziwym sprzątaniu. Wcześniej ten sam komunikat wracał co 5 minut na zmianę z „Czekam”.
- Nowe pozycje **Oświetlenie wewnętrzne** 1.0.0 (`oswietlenie_wewnetrzne.yaml`, wersje `_en` i `_de`, jedna automatyzacja na pomieszczenie) i **Oświetlenie zewnętrzne** 1.0.0 (`oswietlenie_zewnetrzne.yaml`, wersje `_en` i `_de`). Obie bez pomocników i bez pogody.
  - Wewnętrzne: zapalanie przy obecności, gdy jest ciemno (czujnik jasności sprawdzany tylko przy zgaszonych lampach, poniżej połowy progu od razu, bliżej progu po 2 minutach; bez czujnika od zachodu słońca), gaszenie po ustawionym czasie bez obecności, który podwaja się przy powrocie najpóźniej minutę po zgaszeniu (do limitu). Lampy ze ściemnianiem (według `supported_color_modes`) przygasają do połowy 15 s przed zgaszeniem, obecność przywraca jasność; przełączniki nigdy nie przygasają. Ręczne zgaszenie wygrywa do końca obecności, ręcznie zapalone światło świeci co najmniej 30 minut (rozpoznanie po kontekście zmiany lampy). Tryb „Tylko gaś”, noc według ciszy nocnej (lampy nocne na ustawionej jasności albo „Nocą nie zapalaj”), opcja „Zapalaj tylko, gdy ktoś jest w domu”.
  - Zewnętrzne: od zmierzchu do godziny, od zmierzchu do świtu albo tylko przy ruchu (zmierzch i świt z wysokości słońca, −2°). Ruch tylko po zmierzchu: pełne światło przez ustawiony czas po ostatnim ruchu, także w ciszy nocnej. Opcjonalnie w ciszy nocnej tylko przy ruchu i wszystkie lampy na 100 % przy alarmie włamania, potem powrót do stanu z harmonogramu.
  - Zrzuty formularzy zostaną dodane później.
- Generator tłumaczeń: dwa nowe blueprinty w `PAIRS`.

## 2026-10-17 (4)

- **Alarm – czujniki i tryb nocny** 1.0.0, poprawki przed pierwszym wydaniem. Wejścia bez zmian.
  - Inna centrala niż Smart Service Alarm: automatyzacja pilnuje nocy od uzbrojenia do rana. Przejście centrali w oczekiwanie albo alarm w nocy, także z szybkim powrotem do uzbrojenia na noc, oraz restart Home Assistant w nocy oznaczają: rano bez rozbrojenia i powiadomienie. Zastępuje to regułę „uzbrojenie na noc najpóźniej 15 minut po początku ciszy”, która nie wykrywała krótkiego alarmu na początku nocy.
  - Smart Service Alarm: uzbrojenie z automatyzacji, po którym w nocy był alarm, daje rano powiadomienie „Alarm nie został rozbrojony, bo w nocy był alarm.”.
  - Przegląd czujników o 9:00 nic nie wysyła, gdy trwa wtedy cisza nocna.
  - Teksty powiadomień w brzmieniu zatwierdzonym 17.10.2026 (A1–A16): bezosobowo, „Co zrobić” od wielkiej litery, treść zagrożenia według rodzaju (dym, czad, gaz, woda) bez rodzaju „inne”, „restart systemu”. Wpisy w pomocniku powodu i nazwy kroków też bezosobowo. EN i DE przetłumaczone na nowo.

## 2026-10-17 (3)

- Nowa pozycja **Alarm – czujniki i tryb nocny** 1.0.0 (`alarm_czujniki.yaml`, wersje `_en` i `_de`), jedna automatyzacja na centralę. Działa z centralą Smart Service Alarm (wyzwolenie `smartservice_alarm.trigger` z nazwą czujnika) i z każdą inną centralą `alarm_control_panel` (`alarm_control_panel.alarm_trigger`). Czujniki drzwi i okien wyzwalają alarm przy każdym uzbrojeniu, czujniki ruchu tylko poza domem. Dym, czad, gaz i zalanie zawsze włączają syreny i powiadomienie krytyczne, bez zmiany stanu centrali. Powiadomienie krytyczne (Android: kanał „awarie”, priorytet wysoki; iOS: dźwięk krytyczny) wraca co 2 minuty, najwyżej 5 razy, do naciśnięcia PRZYJĄŁEM, które gasi je na wszystkich telefonach i wysyła „Potwierdzenie: imię”. Syreny na ustawiony czas, cichy alarm przy włamaniu, wyłączanie syren przy rozbrojeniu i po starcie Home Assistant. Opcjonalnie: uzbrajanie na noc według ciszy nocnej z rozbrojeniem rano tylko własnego uzbrojenia, przypomnienie, gdy wszyscy wyszli (przycisk „Uzbrój” tylko przy centrali bez kodu do uzbrojenia, nigdy rozbrojenie z powiadomienia), pilnowanie łączności i baterii czujników (próg 15%), powód decyzji w pomocniku. Zrzut formularza zostanie dodany później.
- Generator tłumaczeń: nowy blueprint w `PAIRS`, wartości mapy `teksty` traktowane jako teksty do tłumaczenia.

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
