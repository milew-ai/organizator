#!/usr/bin/env python3
"""Generator pliku jukatan-2026.ics (kalendarz Google).

Uruchomienie:  python3 generate.py
Wynik:         jukatan-2026.ics  (w tym samym katalogu)

Zasady:
- każde wydarzenie ma lokalną godzinę miejsca odjazdu (strefa w TZID),
  a DTEND jest podane w tej samej strefie, więc czas trwania jest poprawny;
- godziny przylotu w innej strefie opisujemy w DESCRIPTION (lokalnie);
- UID są stałe — po ponownym imporcie Google nadpisze, a nie zdubluje.
"""

import os

CRLF = "\r\n"

TZ = {
    "Europe/Warsaw": [
        "BEGIN:STANDARD",
        "DTSTART:19701025T030000",
        "TZOFFSETFROM:+0200",
        "TZOFFSETTO:+0100",
        "TZNAME:CET",
        "END:STANDARD",
        "BEGIN:DAYLIGHT",
        "DTSTART:19700329T020000",
        "TZOFFSETFROM:+0100",
        "TZOFFSETTO:+0200",
        "TZNAME:CEST",
        "END:DAYLIGHT",
    ],
    "Europe/Madrid": [
        "BEGIN:STANDARD",
        "DTSTART:19701025T030000",
        "TZOFFSETFROM:+0200",
        "TZOFFSETTO:+0100",
        "TZNAME:CET",
        "END:STANDARD",
        "BEGIN:DAYLIGHT",
        "DTSTART:19700329T020000",
        "TZOFFSETFROM:+0100",
        "TZOFFSETTO:+0200",
        "TZNAME:CEST",
        "END:DAYLIGHT",
    ],
    "America/Cancun": [
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:-0500",
        "TZOFFSETTO:-0500",
        "TZNAME:EST",
        "END:STANDARD",
    ],
    "America/Guatemala": [
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:-0600",
        "TZOFFSETTO:-0600",
        "TZNAME:CST",
        "END:STANDARD",
    ],
}

# uid, start, end, strefa, tytuł, opis, alarm (None = brak)
EVENTS = [
    (
        "20261123-auto-suwalki-elk",
        "20261123T160000",
        "20261123T170000",
        "Europe/Warsaw",
        "🚗 Suwałki → Ełk (auto)",
        "40,00 zł. Samochód zostawiony w Ełku przy ul. Por. Władysława Świackiego „Sępa”, 19-300 Ełk.\n"
        "Miejsce: https://maps.app.goo.gl/K2h7s9vSYM6Y6xZP9\n"
        "Dalej: pociąg IC 15110 BIEBRZA 17:47.",
        "-PT15M",
    ),
    (
        "20261123-pociag-biebrza",
        "20261123T174700",
        "20261123T221400",
        "Europe/Warsaw",
        "🚆 Ełk → Gdańsk Wrzeszcz (IC 15110 BIEBRZA)",
        "80,00 zł. Bilet w aplikacji PKP Intercity + PDF na Dysku Google.\n"
        "Przyjazd: Gdańsk Wrzeszcz 22:14 (Gdańsk Główny 22:08 — NIE wysiadać tam).\n"
        "Bez przesiadki, ~4 h 27 min.",
        "-PT30M",
    ),
    (
        "20261123-wrzeszcz-patryk",
        "20261123T221400",
        "20261123T224500",
        "Europe/Warsaw",
        "📍 Gdańsk Wrzeszcz → u Patryka",
        "Wysiadamy na Wrzeszczu 22:14. Potwierdzić wcześniej godzinę i sposób wejścia (domofon/kod).\n"
        "Budzik na 3:00; plecak spakowany pod drzwiami.",
        "-PT15M",
    ),
    (
        "20261124-lot-gdn-mad",
        "20261124T060000",
        "20261124T095500",
        "Europe/Warsaw",
        "✈️ Gdańsk → Madryt",
        "146,60 zł, osobny bilet (bez ochrony przy opóźnieniu).\n"
        "Wyjazd z Gdańska 3:30–4:00, na lotnisku ~4:00. Tylko bagaż podręczny.\n"
        "Przylot: Madryt 9:55 (ta sama strefa, UTC+1). Potem przejście T2 → T1.",
        "-PT3H30M",
    ),
    (
        "20261124-lot-mad-cun",
        "20261124T152000",
        "20261125T022500",
        "Europe/Madrid",
        "✈️ Madryt (T1) → Cancún",
        "314,87 €, Air Europa. Odlot 15:20 czasu Madrytu, przylot 20:25 czasu Cancún (UTC−5).\n"
        "Odprawa online otwarta od 22.11 15:20. Kasa zamyka się 14:20.\n"
        "Po przylocie: sprawdzić pieczątkę i liczbę dni (potrzebne 19, do 12.12).",
        "-PT4H",
    ),
    (
        "20261209-lot-gua-cun",
        "20261209T144000",
        "20261209T162700",
        "America/Guatemala",
        "✈️ Gwatemala (GUA) → Cancún (Volaris Y43931)",
        "Odlot 14:40 czasu Gwatemali (UTC−6), przylot 17:27 czasu Cancún (UTC−5) — strefy różnią się o godzinę.\n"
        "Wyjazd z Antigui 11:00–11:30, na lotnisku ~12:40.\n"
        "Po przylocie: nowa pieczątka wjazdowa do Meksyku, ważna do 10.12.",
        "-PT3H",
    ),
    (
        "20261210-lot-cun-mad",
        "20261210T222500",
        "20261211T072500",
        "America/Cancun",
        "✈️ Cancún → Madryt",
        "329,47 €, Air Europa. Odlot 22:25 czasu Cancún, przylot 11.12 o 13:25 czasu Madrytu.\n"
        "Odprawa online od 8.12 22:25. Kasa zamyka się 21:25.\n"
        "PRZED security: kontrola VISITAX (SATQ, przed schodami) — QR w telefonie offline.",
        "-PT4H",
    ),
    (
        "20261212-lot-mad-waw",
        "20261212T191500",
        "20261212T225000",
        "Europe/Madrid",
        "✈️ Madryt → Warszawa Chopin",
        "46,00 €. Odlot 19:15, przylot 22:50 (ta sama strefa, UTC+1).\n"
        "Na lotnisku 17:00–17:15. Po przylocie: odbiór bagażu i przejście na stanowisko autobusu.",
        "-PT3H",
    ),
    (
        "20261213-autobus-waw-elk",
        "20261213T004500",
        "20261213T044600",
        "Europe/Warsaw",
        "🚌 Warszawa Chopin → Ełk",
        "128,00 zł. Odjazd 0:45 z lotniska Chopina, przyjazd Ełk 4:46.\n"
        "Bilet w telefonie + wydruk. Miejsce przy oknie; śpiwór albo kurtka pod ręką.",
        "-PT45M",
    ),
]

# Pobyt w miejscowościach jako wydarzenia całodniowe. DTEND jest wyłączny,
# zgodnie z RFC 5545 (np. 24–25.11 oznacza noc 24.11 i wymeldowanie 25.11).
# UID pozostają stałe, aby Google Calendar aktualizował wydarzenia po imporcie.
STAYS = [
    ("20261123-nocleg-gdansk", "20261123", "20261124", "Gdańsk", "Nocleg u Patryka"),
    ("20261124-pobyt-cancun", "20261124", "20261125", "Cancún", "Tauch Cancún Centro — 1 noc, pokój Queen dla 2 osób. Zameldowanie 15:00–23:30; wymeldowanie 25.11 do 12:00. Adres: 56 Tauch, 77509 Cancún. Zgłoście wcześniej planowaną godzinę przyjazdu. Przy meldowaniu wymagany dokument ze zdjęciem i karta kredytowa. Ewentualna płatność w MXN według kursu z dnia płatności. Odpowiedzialność za szkody: do MXN 1 500."),
    ("20261125-pobyt-merida", "20261125", "20261128", "Mérida", "3 noce; wyjazd do Palenque 28.11"),
    ("20261128-pobyt-palenque", "20261128", "20261201", "Palenque", "3 noce; wyjazd do Flores 1.12"),
    ("20261201-pobyt-flores", "20261201", "20261203", "Flores", "2 noce; wyjazd do Antigui 3.12"),
    ("20261203-pobyt-antigua", "20261203", "20261206", "Antigua", "3 noce przed trekiem; wymeldowanie rano 6.12"),
    ("20261206-acatenango-oboz", "20261206", "20261207", "Acatenango", "Nocleg w obozie podczas 2-dniowego treku"),
    ("20261207-pobyt-antigua", "20261207", "20261209", "Antigua", "2 noce po zejściu z Acatenango; lot do Cancún 9.12"),
    ("20261209-pobyt-cancun", "20261209", "20261210", "Cancún", "1 noc po przylocie z Gwatemali"),
    ("20261211-pobyt-madryt", "20261211", "20261212", "Madryt", "Pobyt po przylocie; wylot do Warszawy 12.12"),
]


def fold(line: str) -> str:
    """Zawija linię do 75 oktetów (RFC 5545), nie rozcinając znaków UTF-8."""
    out, cur, size = [], [], 0
    limit = 75
    for ch in line:
        b = len(ch.encode("utf-8"))
        if size + b > limit:
            out.append("".join(cur))
            cur, size = [" "], 1
            limit = 75
        cur.append(ch)
        size += b
    out.append("".join(cur))
    return CRLF.join(out)


def esc(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build() -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//organizator//Jukatan 2026//PL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Jukatan 2026",
        "X-WR-CALDESC:Wyjazd 23.11-13.12.2026 — sztywne punkty (bilety kupione).",
    ]
    for name, body in TZ.items():
        lines.append("BEGIN:VTIMEZONE")
        lines.append("TZID:" + name)
        lines.extend(body)
        lines.append("END:VTIMEZONE")

    for uid, start, end, tz, summary, desc, alarm in EVENTS:
        lines += [
            "BEGIN:VEVENT",
            "UID:%s@organizator.milew-ai.github.io" % uid,
            "DTSTAMP:20261121T000000Z",
            "DTSTART;TZID=%s:%s" % (tz, start),
            "DTEND;TZID=%s:%s" % (tz, end),
            "SUMMARY:" + esc(summary),
            "DESCRIPTION:" + esc(desc),
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
        ]
        if alarm:
            lines += [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                "TRIGGER:" + alarm,
                "DESCRIPTION:" + esc(summary),
                "END:VALARM",
            ]
        lines.append("END:VEVENT")

    for uid, start, end, town, desc in STAYS:
        lines += [
            "BEGIN:VEVENT",
            "UID:%s@organizator.milew-ai.github.io" % uid,
            "DTSTAMP:20261121T000000Z",
            "DTSTART;VALUE=DATE:%s" % start,
            "DTEND;VALUE=DATE:%s" % end,
            "SUMMARY:" + esc("📍 Pobyt: " + town),
            "DESCRIPTION:" + esc(desc),
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return CRLF.join(fold(l) for l in lines) + CRLF


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "jukatan-2026.ics")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(build())
    print("zapisano:", os.path.normpath(path))
