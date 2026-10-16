"""Dopracowanie pliku .xlsx po konwersji z LibreOffice.

LibreOffice przy eksporcie do `.xlsx` gubi część ustawień, których nie da się
zapisać w płaskim ODF w sposób w pełni przenośny. Ten skrypt wchodzi do
wewnątrz archiwum `.xlsx` (to zwykły ZIP z XML-em) i poprawia:

1. marginesy wydruku (0,6 cm po bokach, ~0,8 cm góra/dół),
2. zablokowanie pierwszej kolumny („Zamroź" na miesiącu),
3. oczyszczenie reguły listy rozwijanej (bez komunikatu o błędzie).

Użycie:
    python postprocess_xlsx.py <plik.xlsx>
"""
import re
import sys
import zipfile
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Użycie: python postprocess_xlsx.py <plik.xlsx>")
    P = str(Path(sys.argv[1]).resolve())
    TMP = P + ".tmp"

    zin = zipfile.ZipFile(P)
    items = zin.infolist()
    data = {i.filename: zin.read(i.filename) for i in items}
    zin.close()

    s = data["xl/worksheets/sheet1.xml"].decode("utf-8")

    # 1) Marginesy strony (0,6 cm boki, ~0,8 cm góra/dół).
    s2 = re.sub(r"<pageMargins[^>]*/>",
                '<pageMargins left="0.236" right="0.236" top="0.315" bottom="0.315" '
                'header="0.079" footer="0.079"/>', s)
    print("margins updated:", s2 != s)
    s = s2

    # 2) Zamrożenie kolumny z miesiącem.
    old_sel = '<selection pane="topLeft" activeCell="A1" activeCellId="0" sqref="A1"/>'
    new_sel = ('<pane xSplit="1" topLeftCell="B1" activePane="topRight" state="frozen"/>'
               '<selection pane="topRight" activeCell="B1" activeCellId="0" sqref="B1"/>')
    if old_sel in s:
        s = s.replace(old_sel, new_sel)
        print("freeze pane added")

    # 3) Czyszczenie walidacji listy.
    m = re.search(r"<dataValidations.*?</dataValidations>", s, re.S)
    if m:
        blk = m.group(0)
        sq = re.search(r'sqref="([^"]*)"', blk).group(1)
        f1 = re.search(r"<formula1>(.*?)</formula1>", blk, re.S).group(1)
        new = ('<dataValidations count="1"><dataValidation allowBlank="1" showDropDown="0" '
               'showErrorMessage="false" type="list" sqref="' + sq + '">'
               "<formula1>" + f1 + "</formula1></dataValidation></dataValidations>")
        s = s.replace(blk, new)
        print("validation cleaned; sqref:", sq)

    data["xl/worksheets/sheet1.xml"] = s.encode("utf-8")

    with zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as z:
        for i in items:
            z.writestr(i.filename, data[i.filename])
    Path(TMP).replace(P)
    print("rewritten:", P)


if __name__ == "__main__":
    main()
