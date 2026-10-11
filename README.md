# Automatyzacje Smart Service

Gotowe automatyzacje (blueprinty) Home Assistant do ogrodu i domu. Przygotowane przez **Smart Service**. Każdą pozycję importujesz jednym kliknięciem przycisku „Importuj do Home Assistant”, a potem ustawiasz w zwykłym formularzu automatyzacji.

## Katalog

### Ogród

| Automatyzacja | Dla kogo | Import |
|---|---|---|
| [Automatyczne koszenie – każda kosiarka](docs/koszenie.md) | Każdy robot koszący z encją `lawn_mower` (Husqvarna, Worx, Segway, Gardena, Mammotion, Ecovacs i inne) | [![Importuj](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Fkoszenie.yaml) |
| [Worx Vision / RTK – inteligentny harmonogram koszenia](https://github.com/SmartServicePL/worx_vision_cloud_plus_automation) | Worx Vision / Vision Cloud z integracją Worx Vision Cloud PLUS | [![Importuj](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fworx_vision_cloud_plus_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fworx_vision_cloud_plus%2Fsmart_mowing_schedule.yaml) |
| [Inteligentne podlewanie ogrodu – 1 do 12 sekcji](https://github.com/SmartServicePL/smart_irrigation_automation) | Rain Bird RC2 oraz zawory i przekaźniki Sonoff, Shelly, ESPHome | [![Importuj](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml) |

### Dom

| Automatyzacja | Dla kogo | Import |
|---|---|---|
| [Robot sprzątający pod nieobecność – każda marka](docs/roboty-sprzatajace.md) | Każdy robot z encją `vacuum` (Roborock, Ecovacs, Dreame, Xiaomi, Matter i inne) | [![Importuj](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fautomatyzacje-smart-service%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_service%2Froboty_sprzatajace.yaml) |
| [Xiaomi X20 Max – powiadomienia o konserwacji](https://github.com/SmartServicePL/xiaomi-x20-max) | Xiaomi Robot Vacuum X20 Max z integracją Xiaomi X20 Max | [![Importuj](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fxiaomi-x20-max%2Fblob%2Fmain%2Fblueprints%2Fautomation%2FSmartServicePL%2Fx20_max_maintenance.yaml) |

Masz robota Dreame? Zobacz też [Dreame Scheduler](https://github.com/botts7/dreame-scheduler) autorstwa botts7 (MIT).

## Jak zaimportować

1. Kliknij przycisk **Importuj** przy wybranej automatyzacji. Otworzy się strona my.home-assistant.io.
2. Podaj adres swojego Home Assistant, jeśli strona o to poprosi, i potwierdź import.
3. W Home Assistant przejdź do *Ustawienia → Automatyzacje i sceny → Blueprinty*, wybierz zaimportowany blueprint i kliknij **Utwórz automatyzację**.
4. Uzupełnij pola. Opis każdej automatyzacji mówi, jakich pomocników potrzebuje.

Przycisk nie działa? W *Ustawienia → Automatyzacje i sceny → Blueprinty → Importuj blueprint* wklej adres pliku z kolumny „Import”.

## Aktualizacje

Każdy blueprint ma w sobie adres źródła. Nową wersję pobierzesz w Home Assistant: *Blueprinty → menu ⋮ przy blueprincie → Importuj ponownie*. Twoje ustawienia w automatyzacjach zostają.

## Licencja

MIT, © 2026 Smart Service. Szczegóły w pliku [LICENSE](LICENSE).
