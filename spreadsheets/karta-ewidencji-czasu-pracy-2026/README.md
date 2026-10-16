# Karta ewidencji czasu pracy (rocznikowa)

Arkusz Calc/Excel do ewidencji czasu pracy za cały rok: 12 miesięcy, lista
rozwijana kodów nieobecności i automatyczne podsumowania godzin.
Gotowy plik: [`Karta_ewidencji_czasu_pracy_2026.xlsx`](Karta_ewidencji_czasu_pracy_2026.xlsx).

> Ten katalog jest samowystarczalny: sam arkusz (`.xlsx`) **oraz** pełny,
> powtarzalny sposób jego zbudowania (`gen_karta.py`, `postprocess_xlsx.py`, `build.ps1`).

## Spis treści

- [Pliki w katalogu](#pliki-w-katalogu)
- [Jak korzystać z arkusza](#jak-korzystać-z-arkusza)
- [Jak zbudować / odtworzyć arkusz](#jak-zbudować--odtworzyć-arkusz)
- [Jak zrobić własny arkusz w tym stylu](#jak-zrobić-własny-arkusz-w-tym-stylu)
- [Znane ograniczenia](#znane-ograniczenia)
- [Odwołania i źródła](#odwołania-i-źródła)

---

## Pliki w katalogu

| Plik | Rola |
| --- | --- |
| [`Karta_ewidencji_czasu_pracy_2026.xlsx`](Karta_ewidencji_czasu_pracy_2026.xlsx) | **Gotowy arkusz** — to otwierasz i wypełniasz. |
| [`gen_karta.py`](gen_karta.py) | Generator: tworzy arkusz jako płaski ODF (`.fods`). |
| [`postprocess_xlsx.py`](postprocess_xlsx.py) | Poprawki pliku `.xlsx` po konwersji (marginesy, zamrożenie, lista). |
| [`build.ps1`](build.ps1) | Skrypt budujący: generator → LibreOffice → postprocess. |
| `.gitignore` | Pomija `*.fods` (efekt pośredni, odtwarzalny) i pliki `*.tmp`. |

Plik `Karta_ewidencji_czasu_pracy_2026.fods` **nie jest wersjonowany** — powstaje
przy każdym budowaniu.

---

## Jak korzystać z arkusza

Arkusz ma **jeden arkusz** o nazwie `Ewidencja 2026`. Układ od lewej do prawej:

| Kolumny | Zawartość |
| --- | --- |
| `A` | miesiąc (`I`..`XII`) |
| `B`..`AF` | dni 1..31 (lista rozwijana z kodami) |
| `AG`..`AJ` | podsumowania godzin: `Suma`, `w niedziele i święta`, `w nocy`, `nadgodziny` |
| `AK`..`AX` | nieobecności w godzinach — po jednej kolumnie na kod ze słownika |

### Wypełnianie krok po kroku

1. **Otwórz plik** w LibreOffice Calc lub Excelu.
2. **Uzupełnij nagłówek** (wiersze 3–9): imię i nazwisko, stanowisko, jednostka.
   W komórce `C8` (`Godziny od – do`) jest `6:00–14:00,  14:00–22:00` — zmień, jeśli u Ciebie jest inaczej.
3. **Wpisuj dni** w wierszu miesiąca (styczeń = wiersz 13):
   - `8` = dzień pracy,
   - albo wybierz kod z listy rozwijanej (np. `UW`, `L4`, `UŻ`).
4. **Reszta liczy się sama**:
   - kolumny `AG`..`AX` pokazują godziny pracy i nieobecności w rozbiciu na kody,
   - wiersz `RAZEM` (wiersz 25) sumuje cały rok,
   - pod tabelą jest blok urlopu wypoczynkowego (wiersze 27–29).
5. **Wydruk** jest już ustawiony: A4 poziomo, skalowanie do 2 stron w poziomie, stopka z numerem strony.

### Kolory komórek dnia

| Kolor | Znaczenie |
| --- | --- |
| biały | dzień roboczy (`8`) |
| jasnoszary | weekend |
| różowy | święto ustawowo wolne |
| ciemnoszary | dzień poza miesiącem (np. 30 lutego) |

### Blok urlopu — gdzie są wartości

Etykiety są scalone w kolumnach `B:J`, więc **liczby leżą w kolumnie `K`**:

| Komórka | Znaczenie |
| --- | --- |
| `K27` | przysługujące dni urlopu (domyślnie `26`) |
| `K28` | wykorzystane dni: `=SUM(AK13:AK24)/8` |
| `K29` | pozostało: `=K27-K28` |

To wyjaśnia, dlaczego formuła odwołuje się do `K27`/`K28`, a nie do `C27`/`C28`.

### Uwagi praktyczne

- Kolumna `w nocy` (`AI`) **nie ma formuły** — uzupełnia się ją ręcznie. Wynika to z tego,
  że arkusz nie przechowuje godzin „od–do" każdego dnia, więc nie ma z czego ich policzyć.
- Lista rozwijana **celowo nie blokuje** wpisania dowolnego tekstu (brak komunikatu o błędzie),
  więc literówka nie zatrzyma pracy — ale też nie zostanie wychwycona.
- Notki pod tabelą (liczba dni roboczych i lista świąt) są **liczone przez generator**,
  a nie wpisane na sztywno — dla innego roku nadal będą poprawne.

---

## Jak zbudować / odtworzyć arkusz

### Wymagania

- **Python 3.8+** — wystarczy biblioteka standardowa, żadnych `pip install`,
- **LibreOffice** (domyślnie `C:\Program Files\LibreOffice\program\soffice.exe`).

### Szybko (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Inny rok:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -Year 2027
```

### Ręcznie (każdy system)

```sh
# 1. Wygeneruj płaski ODF
python gen_karta.py --year 2026

# 2. Skonwertuj do .xlsx (tryb headless)
soffice --headless --convert-to xlsx --outdir . Karta_ewidencji_czasu_pracy_2026.fods

# 3. Popraw to, czego konwersja nie przeniosła
python postprocess_xlsx.py Karta_ewidencji_czasu_pracy_2026.xlsx
```

### Jak to działa (i dlaczego tak)

1. **[`gen_karta.py`](gen_karta.py)** nie używa żadnej biblioteki do arkuszy.
   Buduje **płaski ODF** (`.fods`) — czyli jeden plik XML w formacie OpenDocument.
   Zaleta: pełna kontrola nad stylami, formułami i walidacjami, zero zależności.
   Wewnątrz jest miniaturowy „DSL" komórek (`cell()`, `merged()`, `row()`, `pad()`),
   a na końcu szablon `office:document`.
   Najważniejsze miejsca: `styles()` (style, wydruk), `build_rows()` (układ),
   `DICT` (słownik kodów), `holidays()` / `workdays_in()` (kalendarz).
2. **LibreOffice** konwertuje `.fods` → `.xlsx`. To on zamienia styl ODF na
   style Office i tłumaczy formuły `of:=` na zapis Excela.
3. **[`postprocess_xlsx.py`](postprocess_xlsx.py)** wchodzi do `.xlsx` (to archiwum
   ZIP z XML-em) i poprawia trzy rzeczy, których nie da się wiarygodnie zapisać
   po stronie ODF: marginesy wydruku, zamrożenie pierwszej kolumny i regułę listy rozwijanej.

### Jak zweryfikować, że przebudowa się zgadza

Konwersja przez LibreOffice może dawać różne bajty (kolejność elementów, znaczniki
czasu w metadanych), więc nie porównuj plików „po bajtach". Porównaj **treść**:
wypakuj `xl/worksheets/sheet1.xml` i `xl/sharedStrings.xml` z obu plików i porównaj
komórki (formuły + wartości), scalenia oraz walidacje.

Sprawdzone dla tego arkusza: plik zbudowany tymi skryptami ma **identyczną treść**
jak zapisany `Karta_ewidencji_czasu_pracy_2026.xlsx` — 596 komórek, ta sama liczba
scaleń (56) oraz te same ustawienia wydruku i walidacji.

---

## Jak zrobić własny arkusz w tym stylu

Ten wzorzec nadaje się do każdego „formularza w arkuszu": kart obecności, rozliczeń,
harmonogramów.

1. **Zaplanuj siatkę**: co jest stałe (nagłówki, etykiety), co jest formułą, a co
   wypełnia użytkownik. Zapisz kolumny literami (`A`, `B`, …, `AA`).
2. **Napisz generator** produkujący `.fods`. Minimalny szkielet to
   `<office:document office:mimetype="application/vnd.oasis.opendocument.spreadsheet">`
   z sekcjami: `office:font-face-decls`, `office:automatic-styles`, `office:master-styles`,
   `office:body > office:spreadsheet > table:table`.
3. **Zdefiniuj style raz** (`ce_*` dla komórek, `co*` dla kolumn). Wzorce do
   podpatrzenia: `ce_day_wkd` (tło weekendu), `ce_sum` (wynik formuły), `coD` (szerokość kolumny).
4. **Generuj wiersze** funkcją zwracającą listę komórek. Używaj `pad()`, żeby każdy
   wiersz miał pełną szerokość — inaczej przesuną się kolumny.
5. **Dodaj listę rozwijaną** przez `table:content-validation` z
   `table:condition="of:cell-content-is-in-list(...)"` i przypisz ją do komórek
   atrybutem `table:content-validation-name`.
6. **Skonwertuj** przez LibreOffice do formatu docelowego (`.xlsx`, `.pdf`).
7. **Dopracuj** w `postprocess` to, czego konwersja nie przeniosła.
8. **Zweryfikuj wygląd**: zrzut do PDF/PNG i obejrzenie go jest szybsze niż
   klikanie po arkuszu.

### Najczęstsze modyfikacje

| Chcę zmienić… | Gdzie |
| --- | --- |
| rok | `--year`, albo `YEAR` w [`gen_karta.py`](gen_karta.py) |
| godziny pracy | lista `info` w `build_rows()` |
| kody nieobecności | lista `DICT` (kolejność = kolejność kolumn) |
| szerokości kolumn | `coD` oraz lista `widths` w `styles()` |
| podział na strony | `style:scale-to-X/Y` i `fo:break-before` w `styles()` |

---

## Znane ograniczenia

- Kolumna `w nocy` (`AI`) nie ma formuły — to świadome, patrz [wyżej](#uwagi-praktyczne).
- Walidacja listy ma wyłączony komunikat o błędzie: błędny kod przejdzie bez ostrzeżenia.
- Arkusz obsługuje jeden rok i jedno stanowisko (jeden blok nagłówka).
- `N_DAYS` jest stałe (31); obsługa mniej/mniej niż 31 dni wymaga zmian w generatorze.
- Weryfikacja końcowa to porównanie treści XML, a nie automatyczny test jednostkowy.

---

## Odwołania i źródła

### Dokumentacja zewnętrzna

- **OpenDocument (ODF) 1.3** — specyfikacja formatu `.fods`: <https://docs.oasis-open.org/office/OpenDocument/v1.3/>
- **ODF 1.3, część 3 (schemat + OpenFormula)** — składnia formuł `of:=`, walidacje, style:
  <https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-schema/OpenDocument-v1.3-os-part3-schema.html>
- **Komitet OASIS ODF TC** (gdzie powstaje standard): <https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=office>
- **LibreOffice — parametry wiersza poleceń** (`--headless`, `--convert-to`, `-env:UserInstallation`):
  <https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html>
- **Python — `zipfile`** (obróbka `.xlsx` jako ZIP): <https://docs.python.org/3/library/zipfile.html>
- **Python — `argparse`**: <https://docs.python.org/3/library/argparse.html>

### Materiały w repozytorium

- [README repozytorium](../README.md) — opis projektu i struktury.
- [AGENTS.md](../AGENTS.md) — standardy pracy w tym repozytorium.
- [skills/git-ssh-setup/SKILL.md](../skills/git-ssh-setup/SKILL.md) — skill agenta do konfiguracji SSH/GitHub.

### Podstawa kodów nieobecności

Skróty w nawiasach (np. `U:WP`, `U:NŻ`, `O:ND`, `W:N`) pochodzą ze **słownika w oryginalnym
arkuszu** i wyglądają na nazwy z systemu kadrowo-płacowego — nie na oznaczenia z przepisów.
Ogólna podstawa prawna poszczególnych nieobecności to:

- **Kodeks pracy** — urlopy i zwolnienia okolicznościowe, opieka nad dzieckiem, nadgodziny:
  <https://pl.wikipedia.org/wiki/Kodeks_pracy> · tekst urzędowy (ISAP): <https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU19740240141>
- **Urlop wypoczynkowy** (wymiar, zasady): <https://pl.wikipedia.org/wiki/Urlop_wypoczynkowy>

> ⚠️ Dokładne mapowanie skrótów na konkretne przepisy **należy potwierdzić** z działem kadr —
> w repozytorium nie ma źródła, z którego ten słownik pochodzi.

---

## Środowisko

Budowanie testowano na Windows z LibreOffice w trybie `--headless`, na osobnym,
tymczasowym profilu (`-env:UserInstallation`), żeby nie kolidować z otwartą instancją
LibreOffice. Skrypt `build.ps1` sprząta ten profil po zakończeniu i przerywa pracę
przy pierwszym błędzie (sprawdza kod wyjścia każdego polecenia).
