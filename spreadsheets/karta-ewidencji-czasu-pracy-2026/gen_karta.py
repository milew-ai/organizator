"""Generator arkusza „Karta ewidencji czasu pracy" (rok konfigurowalny).

Skrypt buduje **płaski plik ODF** (`.fods`) — to zwykły XML, więc nie trzeba
żadnej biblioteki do arkuszy. Konwersję do `.xlsx` wykonuje LibreOffice
(patrz `build.ps1`).

Użycie:
    python gen_karta.py --year 2026
    python gen_karta.py --year 2026 --out "C:\\sciezka\\plik.fods"

Struktura arkusza (jeden arkusz, od lewej do prawej):
    A          – nazwa miesiąca (I..XII)
    B..AF      – dni 1..31 (lista rozwijana z kodami)
    AG..AJ     – podsumowania godzin (Suma, w niedziele/święta, w nocy, nadgodziny)
    AK..AX     – nieobecności w godzinach, po jednej kolumnie na kod ze słownika
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

# --- Konfiguracja -----------------------------------------------------------

ROMANS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Słownik kodów: (kod, opis). Pierwszy wpis to praca; każdy kolejny kod
# dostaje własną kolumnę w sekcji „Nieobecności w godzinach".
DICT = [
    (8, "Praca – 8 godzin"),
    ("UW", "Urlop wypoczynkowy (U:WP)"),
    ("UŻ", "Urlop „na żądanie” (U:NŻ)"),
    ("UO", "Urlop okolicznościowy (U:O)"),
    ("UB", "Urlop bezpłatny (U:B)"),
    ("OND", "Opieka nad dzieckiem (O:ND)"),
    ("L4", "Zwolnienie lekarskie (L4)"),
    ("UWW", "Urlop wychowawczy (U:W)"),
    ("UM", "Urlop macierzyński (U:M)"),
    ("ŚR", "Świadczenia rehabilitacyjne (Ś:Reh)"),
    ("OK", "Oddanie krwi (O:K)"),
    ("WN", "Wolne za nadgodziny (W:N)"),
    ("WŚ", "Odbiór za pracę w święto (O:DB)"),
    ("W5", "Wolne – 5-dniowy tydzień pracy (W:5)"),
    ("DN", "Wypłata nadgodzin (D:N)"),
]
ABSENCE = [c for c, _ in DICT[1:]]              # kody, które dostają kolumnę
HOUR_HEADS = ["Suma", "w niedziele\ni święta", "w nocy", "nad-\ngodziny"]
SUM_HEADS = HOUR_HEADS + ABSENCE

N_DAYS = 31
FIRST_SUM = 2 + N_DAYS                          # pierwsza kolumna podsumowań (AG)
TOTAL_COLS = 1 + N_DAYS + len(SUM_HEADS)
MONTH_ROW0 = 13                                 # wiersz miesiąca „I"
DV = "dvKody"                                   # nazwa reguły walidacji listy

# Ustawiane w main():
YEAR = 2026
SHEET = "Ewidencja 2026"


def easter(year: int) -> date:
    """Niedziela wielkanocna (algorytm Gaussa)."""
    a = year % 19; b = year // 100; c = year % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return date(year, (h + l - 7 * m + 114) // 31, ((h + l - 7 * m + 114) % 31) + 1)


def holidays(year: int) -> set:
    """Święta ustawowo wolne (Wielkanoc liczona, nie na sztywno)."""
    e = easter(year)
    return {date(year, 1, 1), date(year, 1, 6), e, e + timedelta(days=1), date(year, 5, 1),
            date(year, 5, 3), e + timedelta(days=60), date(year, 8, 15), date(year, 11, 1),
            date(year, 11, 11), date(year, 12, 24), date(year, 12, 25), date(year, 12, 26)}


def workdays_in(year: int) -> int:
    """Dni robocze w roku = dni powszednie, które nie są świętami."""
    hols = holidays(year)
    d, end, n = date(year, 1, 1), date(year, 12, 31), 0
    while d <= end:
        if d.weekday() < 5 and d not in hols:
            n += 1
        d += timedelta(days=1)
    return n


def holiday_labels(year: int) -> list:
    """Święta w kolejności chronologicznej, jako etykiety „dzień miesiąc"."""
    e = easter(year)
    out = []
    for d in sorted(holidays(year)):
        label = f"{d.day} {ROMANS[d.month - 1]}"
        if d == e:
            label += " (Wielkanoc)"
        elif d == date(year, 12, 24):
            label += " (Wigilia)"
        out.append(label)
    return out


def col_letter(n: int) -> str:
    """1 -> A, 27 -> AA ..."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr(t: str) -> str:
    return esc(t).replace('"', "&quot;")


# --- Miniaturowy DSL komórek (zwraca fragmenty XML) --------------------------

def cell(style=None, text=None, value=None, formula=None, colspan=1, rowspan=1, dv=False):
    a = ""
    if style:
        a += f' table:style-name="{style}"'
    if colspan > 1:
        a += f' table:number-columns-spanned="{colspan}"'
    if rowspan > 1:
        a += f' table:number-rows-spanned="{rowspan}"'
    if formula is not None:
        a += f' table:formula="{attr(formula)}"'
    elif value is not None:
        a += f' office:value-type="float" office:value="{value}"'
    elif text is not None:
        a += ' office:value-type="string"'
    if dv:
        a += f' table:content-validation-name="{DV}"'
    body = f"<text:p>{esc(text)}</text:p>" if text is not None else ""
    return f"<table:table-cell{a}>{body}</table:table-cell>"


def covered(n):
    return "<table:covered-table-cell/>" * n


def merged(style, text, width, rowspan=1):
    """Komórka scalona poziomo o zadanej szerokości."""
    return cell(style, text=text, colspan=width, rowspan=rowspan) + covered(width - 1)


def row(style, cells):
    return f'<table:table-row table:style-name="{style}">{cells}</table:table-row>'


def pad(parts, used, style="ce_plain"):
    """Dopełnia wiersz pustymi komórkami do pełnej szerokości arkusza."""
    extra = TOTAL_COLS - used
    assert extra >= 0, f"too many columns: {used}"
    return "".join(parts) + cell(style) * extra


# --- Style -------------------------------------------------------------------

def styles() -> str:
    out = [
        '<number:number-style style:name="Nint"><number:number number:decimal-places="0" '
        'number:min-integer-digits="1"/></number:number-style>',
        '<style:style style:name="ce_plain" style:family="table-cell"/>',
        '<style:style style:name="ce_title" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.1cm" style:vertical-align="middle"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="14pt" '
        'fo:color="#1F3864"/></style:style>',
        '<style:style style:name="ce_lbl" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.05cm"/><style:paragraph-properties fo:text-align="left"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="10pt"/></style:style>',
        '<style:style style:name="ce_val" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.05cm" fo:border-bottom="0.5pt solid #808080" '
        'style:vertical-align="middle"/><style:paragraph-properties fo:text-align="left"/>'
        '<style:text-properties style:font-name="Calibri" fo:font-size="10pt"/></style:style>',
        '<style:style style:name="ce_gh" style:family="table-cell">'
        '<style:table-cell-properties fo:background-color="#D9E2F3" fo:padding="0.06cm" '
        'fo:border="0.5pt solid #7f7f7f" style:vertical-align="middle"/>'
        '<style:paragraph-properties fo:text-align="center" fo:wrap-option="wrap"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="10pt"/></style:style>',
        '<style:style style:name="ce_mh" style:family="table-cell">'
        '<style:table-cell-properties fo:background-color="#EDEDED" fo:padding="0.03cm" '
        'fo:border="0.5pt solid #9f9f9f" style:vertical-align="middle"/>'
        '<style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="8pt"/></style:style>',
        '<style:style style:name="ce_sumh" style:family="table-cell">'
        '<style:table-cell-properties fo:background-color="#D9E2F3" fo:padding="0.03cm" '
        'fo:border="0.5pt solid #7f7f7f" style:vertical-align="middle" fo:wrap-option="wrap"/>'
        '<style:paragraph-properties fo:text-align="center" fo:wrap-option="wrap"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="8pt"/></style:style>',
        '<style:style style:name="ce_day" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.02cm" fo:border="0.5pt solid #c8c8c8" '
        'style:vertical-align="middle"/><style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="ce_day_wkd" style:family="table-cell" style:parent-style-name="ce_day">'
        '<style:table-cell-properties fo:background-color="#F2F2F2"/></style:style>',
        '<style:style style:name="ce_day_hol" style:family="table-cell" style:parent-style-name="ce_day">'
        '<style:table-cell-properties fo:background-color="#F8D7DA"/></style:style>',
        '<style:style style:name="ce_day_off" style:family="table-cell" style:parent-style-name="ce_day">'
        '<style:table-cell-properties fo:background-color="#D0D0D0"/></style:style>',
        '<style:style style:name="ce_mon" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.05cm" fo:border="0.5pt solid #7f7f7f" '
        'fo:background-color="#EDEDED" style:vertical-align="middle"/>'
        '<style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="10pt"/></style:style>',
        '<style:style style:name="ce_sum" style:family="table-cell" style:data-style-name="Nint">'
        '<style:table-cell-properties fo:padding="0.03cm" fo:border="0.5pt solid #c8c8c8" '
        'style:vertical-align="middle"/><style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="ce_summan" style:family="table-cell" style:parent-style-name="ce_sum">'
        '<style:table-cell-properties fo:background-color="#FFF2CC"/></style:style>',
        '<style:style style:name="ce_sumsum" style:family="table-cell" style:parent-style-name="ce_sum">'
        '<style:table-cell-properties fo:background-color="#E2EFDA"/></style:style>',
        '<style:style style:name="ce_tot" style:family="table-cell" style:data-style-name="Nint">'
        '<style:table-cell-properties fo:padding="0.04cm" fo:border="0.5pt solid #7f7f7f" '
        'fo:background-color="#D9E2F3" style:vertical-align="middle"/>'
        '<style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="ce_totlbl" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.05cm" fo:border="0.5pt solid #7f7f7f" '
        'fo:background-color="#D9E2F3" style:vertical-align="middle"/>'
        '<style:paragraph-properties fo:text-align="left"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="10pt"/></style:style>',
        '<style:style style:name="ce_dictc" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.03cm" fo:border="0.5pt solid #d0d0d0"/>'
        '<style:paragraph-properties fo:text-align="center"/>'
        '<style:text-properties fo:font-weight="bold" style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="ce_dictd" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.03cm" fo:border="0.5pt solid #d0d0d0"/>'
        '<style:paragraph-properties fo:text-align="left"/>'
        '<style:text-properties fo:color="#404040" style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="ce_note" style:family="table-cell">'
        '<style:table-cell-properties fo:padding="0.05cm"/><style:paragraph-properties '
        'fo:text-align="left" fo:wrap-option="wrap"/><style:text-properties fo:font-style="italic" '
        'fo:color="#595959" style:font-name="Calibri" fo:font-size="9pt"/></style:style>',
        '<style:style style:name="coM" style:family="table-column">'
        '<style:table-column-properties style:column-width="1.3cm"/></style:style>',
        '<style:style style:name="coD" style:family="table-column">'
        '<style:table-column-properties style:column-width="0.81cm"/></style:style>',
        # Ustawienia wydruku: A4 poziomo, skalowane do 2 stron w poziomie x 1 w pionie.
        '<style:style style:name="ta1" style:family="table" style:master-page-name="PageStyle1">'
        '<style:table-properties style:writing-mode="lr-tb" table:display="true"/></style:style>',
        '<style:page-layout style:name="pm1">'
        '<style:page-layout-properties fo:page-width="29.7cm" fo:page-height="21cm" '
        'style:print-orientation="landscape" '
        'fo:margin-top="0.7cm" fo:margin-bottom="0.7cm" fo:margin-left="0.6cm" fo:margin-right="0.6cm" '
        'style:scale-to-X="2" style:scale-to-Y="1" style:writing-mode="lr-tb" '
        'style:table-centering="horizontal"/></style:page-layout>',
    ]
    # Kolumny sekcji nieobecności; przed piątą wymuszamy podział strony.
    widths = ["2.0cm", "2.2cm", "1.4cm", "2.0cm"] + ["1.15cm"] * len(ABSENCE)
    for i, w in enumerate(widths, start=1):
        bb = ' fo:break-before="page"' if i == 5 else ""
        out.append(f'<style:style style:name="coS{i}" style:family="table-column">'
                   f'<style:table-column-properties{bb} style:column-width="{w}"/></style:style>')
    out.append('<style:style style:name="ro" style:family="table-row">'
               '<style:table-row-properties style:row-height="0.42cm" style:use-optimal-row-height="true"/>'
               "</style:style>")
    return "".join(out)


def hour_expr(r):
    """Wartość godzinowa komórki: liczba albo „8" dla kodu pracy, inaczej 0."""
    return f'IF(ISNUMBER([.{r}]);[.{r}];IF([.{r}]="8";8;0))'


# --- Budowa wierszy ----------------------------------------------------------

def build_rows():
    holidays_set = holidays(YEAR)
    rows = []
    rows.append(row("ro", pad([cell("ce_plain"), merged("ce_title",
        f"Karta ewidencji czasu pracy – rok {YEAR} (pełen etat, poniedziałek–piątek, 8 h)", TOTAL_COLS - 1)], TOTAL_COLS)))
    rows.append(row("ro", cell("ce_plain") * TOTAL_COLS))

    # Nagłówek z danymi pracownika / jednostki.
    info = [("Imię i nazwisko", ""), ("Stanowisko", ""), ("Jednostka organizacyjna", ""),
            ("Rok", YEAR), ("Norma", "Pełen etat – 8 h/dzień, poniedziałek–piątek"),
            ("Godziny od – do", "6:00–14:00,  14:00–22:00"), ("Ilość godzin na dzień", 8)]
    LBL_W, VAL_W = 6, 12
    for label, value in info:
        if isinstance(value, int):
            val = cell("ce_val", text=str(value), value=value, colspan=VAL_W) + covered(VAL_W - 1)
        else:
            val = merged("ce_val", value, VAL_W)
        rows.append(row("ro", pad([cell("ce_plain"), merged("ce_lbl", label, LBL_W), val], 1 + LBL_W + VAL_W)))

    rows.append(row("ro", cell("ce_plain") * TOTAL_COLS))

    # Nagłówki: miesiąc / dni / podsumowania / nieobecności.
    rows.append(row("ro", pad([
        cell("ce_gh", text="Miesiąc", rowspan=2),
        merged("ce_gh", "Dni miesiąca – wybierz z listy (8 = praca, inaczej kod nieobecności)", N_DAYS),
        merged("ce_gh", "Ilość godzin pracy", 4),
        merged("ce_gh", "Nieobecności w godzinach (8 h za każdy dzień z kodem)", len(ABSENCE)),
    ], TOTAL_COLS)))

    parts = [covered(1)]
    parts += [cell("ce_mh", text=str(d)) for d in range(1, 32)]
    parts += [cell("ce_sumh", text=h) for h in HOUR_HEADS]
    # Nagłówki nieobecności to formuły wskazujące kody ze słownika – wstawiane później.
    parts += [cell("ce_sumh") for _ in ABSENCE]
    rows.append(row("ro", "".join(parts)))

    # 12 wierszy miesięcy.
    for m in range(1, 13):
        r = MONTH_ROW0 + (m - 1)
        parts = [cell("ce_mon", text=ROMANS[m - 1])]
        we_cols = []                            # kolumny weekendów/świąt
        for d in range(1, 32):
            if d > MONTH_DAYS[m - 1]:
                parts.append(cell("ce_day_off"))
                continue
            dt = date(YEAR, m, d)
            if dt in holidays_set:
                parts.append(cell("ce_day_hol", dv=True)); we_cols.append(col_letter(1 + d))
            elif dt.weekday() >= 5:
                parts.append(cell("ce_day_wkd", dv=True)); we_cols.append(col_letter(1 + d))
            else:
                parts.append(cell("ce_day", text="8", value=8, dv=True))
        rng = f"[.B{r}:.AF{r}]"
        parts.append(cell("ce_sumsum", formula=f'of:=SUMPRODUCT(IF(ISNUMBER({rng});{rng};IF({rng}="8";8;0)))'))
        parts.append(cell("ce_sum", formula="of:=SUM(" + ";".join(hour_expr(f"{c}{r}") for c in we_cols) + ")"))
        parts.append(cell("ce_summan"))
        parts.append(cell("ce_sum", formula=f'of:=SUMIF({rng};">8")-8*COUNTIF({rng};">8")'))
        for j in range(len(ABSENCE)):
            parts.append(cell("ce_sum", formula=f'of:=COUNTIF({rng};[.$B${31 + 1 + j + 1}])*8'))
        rows.append(row("ro", "".join(parts)))

    # Wiersz RAZEM.
    m0, m1 = MONTH_ROW0, MONTH_ROW0 + 11
    parts = [cell("ce_totlbl", text="RAZEM")] + [cell("ce_plain")] * N_DAYS
    for j in range(len(SUM_HEADS)):
        col = col_letter(FIRST_SUM + j)
        parts.append(cell("ce_tot", formula=f"of:=SUM([.{col}{m0}:.{col}{m1}])"))
    rows.append(row("ro", "".join(parts)))
    rows.append(row("ro", cell("ce_plain") * TOTAL_COLS))

    # Podsumowanie urlopu wypoczynkowego.
    # Uwaga: etykieta jest scalona w B:J, więc WARTOŚCI leżą w kolumnie K
    # (stąd odwołania K27/K28 w formule „Pozostało").
    uw = col_letter(FIRST_SUM + 4)
    LW = 9
    rows.append(row("ro", pad([cell("ce_plain"), merged("ce_lbl", "Przysługujące dni urlopu wypoczynkowego:", LW),
                               cell("ce_val", text="26", value=26)], 1 + LW + 1)))
    rows.append(row("ro", pad([cell("ce_plain"), merged("ce_lbl", "Wykorzystano dni urlopu wypoczynkowego:", LW),
                               cell("ce_val", formula=f"of:=SUM([.{uw}{m0}:.{uw}{m1}])/8")], 1 + LW + 1)))
    rows.append(row("ro", pad([cell("ce_plain"), merged("ce_lbl", "Pozostało dni urlopu wypoczynkowego:", LW),
                               cell("ce_val", formula="of:=K27-K28")], 1 + LW + 1)))
    rows.append(row("ro", cell("ce_plain") * TOTAL_COLS))

    # Słownik kodów.
    rows.append(row("ro", pad([cell("ce_plain"), merged("ce_lbl",
        "Słownik kodów (lista rozwijana w komórkach dni; 8 = praca, reszta = nieobecność):", 24)], 1 + 24)))

    dict_start = len(rows) + 1
    for idx, (code, desc) in enumerate(DICT):
        if isinstance(code, int):
            cc = cell("ce_dictc", text=str(code), value=code, colspan=2) + covered(1)
        else:
            cc = merged("ce_dictc", str(code), 2)
        rows.append(row("ro", pad([cell("ce_plain"), cc, merged("ce_dictd", desc, 15)], 1 + 2 + 15)))
    dict_end = len(rows)

    rows.append(row("ro", cell("ce_plain") * TOTAL_COLS))
    NW = 35                                     # kolumny B..AJ = pierwsza strona wydruku
    wd = workdays_in(YEAR)
    notes = [
        "Słownik kodów: wpisz lub wybierz kod w komórce dnia – odpowiednia kolumna pokaże 8 h "
        "(np. UW = urlop wypoczynkowy). 8 = dzień pracy.",
        f"Godziny pracy: {wd} dni robocze × 8 h = {wd * 8} h (pełen etat). "
        "Dni wolne: szary = weekend, różowy = święto.",
        f"Święta {YEAR}: " + ", ".join(holiday_labels(YEAR)) + ".",
    ]
    for n in notes:
        rows.append(row("ro", pad([cell("ce_plain"), merged("ce_note", n, NW)], 1 + NW)))
    return "".join(rows), dict_start, dict_end


def main() -> None:
    global YEAR, SHEET
    ap = argparse.ArgumentParser(description="Generator karty ewidencji czasu pracy (.fods).")
    ap.add_argument("--year", type=int, default=2026, help="rok arkusza (domyślnie 2026)")
    ap.add_argument("--out", default=None, help="ścieżka wynikowego pliku .fods")
    args = ap.parse_args()

    YEAR = args.year
    SHEET = f"Ewidencja {YEAR}"
    out_path = Path(args.out) if args.out else Path(__file__).resolve().parent / f"Karta_ewidencji_czasu_pracy_{YEAR}.fods"

    body, dict_start, dict_end = build_rows()

    # Nagłówki nieobecności: formuły pokazujące kody ze słownika.
    header_cells = []
    for j in range(len(ABSENCE)):
        header_cells.append(
            f'<table:table-cell table:style-name="ce_sumh" table:formula="of:=[.$B${dict_start + 1 + j}]"/>'
        )
    placeholder = cell("ce_sumh") * len(ABSENCE)
    assert body.count(placeholder) == 1, body.count(placeholder)
    body = body.replace(placeholder, "".join(header_cells), 1)

    cols = (
        '<table:table-header-columns><table:table-column table:style-name="coM"/></table:table-header-columns>'
        '<table:table-column table:style-name="coD" table:number-columns-repeated="31"/>'
        + "".join(f'<table:table-column table:style-name="coS{i}"/>' for i in range(1, len(SUM_HEADS) + 1))
    )
    validations = (
        '<table:content-validations><table:content-validation table:name="' + DV + '" '
        f'table:condition="of:cell-content-is-in-list([.$B${dict_start}:.$B${dict_end}])" '
        'table:allow-empty-cell="true" table:display-list="unsorted" '
        f'table:base-cell-address="\'{SHEET}\'.B{MONTH_ROW0}"/></table:content-validations>'
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
    xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
    xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
    office:version="1.2"
    office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
  <office:font-face-decls><style:font-face style:name="Calibri" svg:font-family="Calibri"/></office:font-face-decls>
  <office:automatic-styles>{styles()}</office:automatic-styles>
  <office:master-styles>
    <style:master-page style:name="PageStyle1" style:page-layout-name="pm1">
      <style:footer><text:p>Karta ewidencji czasu pracy {YEAR}  |  strona <text:page-number>1</text:page-number></text:p></style:footer>
    </style:master-page>
  </office:master-styles>
  <office:body>
    <office:spreadsheet>
      <table:calculation-settings table:case-sensitive="false" table:automatic-find-labels="false"
          table:use-regular-expressions="false" table:use-wildcards="true"/>
      {validations}
      <table:table table:name="{SHEET}" table:style-name="ta1">
        {cols}
        {body}
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>
"""
    out_path.write_text(xml, encoding="utf-8")
    print(f"Zapisano -> {out_path}")
    print(f"Kody z kolumnami: {len(ABSENCE)} | słownik wiersze {dict_start}-{dict_end} | kolumn: {TOTAL_COLS}")


if __name__ == "__main__":
    main()
