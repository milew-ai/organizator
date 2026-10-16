# Arkusze (`spreadsheets/`)

Katalog na generowane arkusze. Każdy podkatalog to **osobny, samowystarczalny projekt**:
gotowy plik `.xlsx` + generator + instrukcja obsługi i budowania.

| Arkusz | Rok | Katalog | Opis |
| --- | --- | --- | --- |
| Karta ewidencji czasu pracy | 2026 | [karta-ewidencji-czasu-pracy-2026/](karta-ewidencji-czasu-pracy-2026/README.md) | 12 miesięcy, kody nieobecności, automatyczne sumy godzin i rozliczenie urlopu |

## Jak dodać kolejny arkusz

1. Utwórz podkatalog `spreadsheets/<nazwa>/`.
2. Wrzuć: gotowy `.xlsx` i towarzyszący mu `.fods`, generator (`gen_*.py`),
   post-processing (`postprocess_*.py`), skrypt budujący (`build.ps1`) oraz `.gitignore`.
3. Napisz `README.md` według wzoru z
   [karta-ewidencji-czasu-pracy-2026/README.md](karta-ewidencji-czasu-pracy-2026/README.md).
4. Dopisz wiersz w tabeli powyżej.

Ogólny wzorzec (ODF → LibreOffice → postprocess) i instrukcja „jak zrobić własny arkusz
w tym stylu" znajdują się w sekcji
[Jak zrobić własny arkusz w tym stylu](karta-ewidencji-czasu-pracy-2026/README.md#jak-zrobić-własny-arkusz-w-tym-stylu).
