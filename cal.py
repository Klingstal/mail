#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional

import requests
from icalendar import Calendar, Event

POSTAL_CODE = "56632"
API_URL = f"https://portal.postnord.com/api/sendoutarrival/closest?postalCode={POSTAL_CODE}"
OUTPUT_PATH = Path("docs/calendar.ics")
CAL_NAME = f"Postutdelning {POSTAL_CODE}"

MONTHS_SV = {
    "januari": 1, "februari": 2, "mars": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "augusti": 8, "september": 9, "oktober": 10, "november": 11, "december": 12
}
DATE_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-zÅÄÖåäö]+),?\s+(\d{4})\s*$")

def parse_postnord_date(s: str) -> Optional[date]:
    if not s:
        return None
    s = s.strip()
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            return datetime.fromisoformat(s).date()
    except Exception:
        pass
    m = DATE_RE.match(s)
    if m:
        day, month_name, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = MONTHS_SV.get(month_name)
        if month:
            return date(year, month, day)
    return None

def fetch_delivery_data() -> dict:
    resp = requests.get(API_URL, timeout=20)
    resp.raise_for_status()
    return resp.json()

def build_calendar(dates):
    cal = Calendar()
    cal.add("prodid", "-//PostNord Utdelningskalender//postnord.se//")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", CAL_NAME)
    cal.add("X-WR-TIMEZONE", "Europe/Stockholm")
    for d in sorted(set(dates)):
        event = Event()
        event.add("summary", "Postutdelning")
        event.add("dtstart", d)
        event.add("dtend", d + timedelta(days=1))
        event.add("dtstamp", datetime.utcnow())
        uid = f"postnord-{POSTAL_CODE}-{d.isoformat()}@example.local"
        event.add("uid", uid)
        event.add("url", "https://www.postnord.se/vara-verktyg/sok-utdelningsdag/")
        cal.add_component(event)
    return cal

def main() -> int:
    try:
        data = fetch_delivery_data()
    except Exception as e:
        print(f"Misslyckades att hämta data: {e}", file=sys.stderr)
        return 1
    delivery_str = data.get("delivery")
    upcoming = data.get("upcoming")
    if isinstance(upcoming, str):
        upcoming_list = [upcoming]
    else:
        upcoming_list = list(upcoming or [])
    dates = []
    d1 = parse_postnord_date(delivery_str)
    if d1: dates.append(d1)
    for s in upcoming_list:
        d2 = parse_postnord_date(s)
        if d2: dates.append(d2)
    if not dates:
        print("Inga giltiga datum hittades.")
        return 2
    cal = build_calendar(dates)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(cal.to_ical())
    print(f"Skrev {OUTPUT_PATH} med {len(set(dates))} händelse(r).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

import requests
from icalendar import Calendar, Event

POSTAL_CODE = "56632"
API_URL = f"https://portal.postnord.com/api/sendoutarrival/closest?postalCode={POSTAL_CODE}"
OUTPUT_PATH = Path("docs/calendar.ics")
CAL_NAME = f"Postutdelning {POSTAL_CODE}"

MONTHS_SV = {
    "januari": 1, "februari": 2, "mars": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "augusti": 8, "september": 9, "oktober": 10, "november": 11, "december": 12
}
DATE_RE = re.compile(r"^\s*(\d{1,2})\s+([A-Za-zÅÄÖåäö]+),?\s+(\d{4})\s*$")

def parse_postnord_date(s: str) -> date | None:
    if not s:
        return None
    s = s.strip()
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            return datetime.fromisoformat(s).date()
    except Exception:
        pass
    m = DATE_RE.match(s)
    if m:
        day, month_name, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        month = MONTHS_SV.get(month_name)
        if month:
            return date(year, month, day)
    return None

def fetch_delivery_data() -> dict:
    resp = requests.get(API_URL, timeout=20)
    resp.raise_for_status()
    return resp.json()

def build_calendar(dates: list[date]) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//PostNord Utdelningskalender//postnord.se//")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", CAL_NAME)
    cal.add("X-WR-TIMEZONE", "Europe/Stockholm")
    for d in sorted(set(dates)):
        event = Event()
        event.add("summary", "Postutdelning")
        event.add("dtstart", d)
        event.add("dtend", d + timedelta(days=1))
        event.add("dtstamp", datetime.utcnow())
        uid = f"postnord-{POSTAL_CODE}-{d.isoformat()}@example.local"
        event.add("uid", uid)
        event.add("url", "https://www.postnord.se/vara-verktyg/sok-utdelningsdag/")
        cal.add_component(event)
    return cal

def main() -> int:
    try:
        data = fetch_delivery_data()
    except Exception as e:
        print(f"Misslyckades att hämta data: {e}", file=sys.stderr)
        return 1
    delivery_str = data.get("delivery")
    upcoming = data.get("upcoming")
    if isinstance(upcoming, str):
        upcoming_list = [upcoming]
    else:
        upcoming_list = list(upcoming or [])
    dates = []
    d1 = parse_postnord_date(delivery_str)
    if d1: dates.append(d1)
    for s in upcoming_list:
        d2 = parse_postnord_date(s)
        if d2: dates.append(d2)
    if not dates:
        print("Inga giltiga datum hittades.")
        return 2
    cal = build_calendar(dates)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(cal.to_ical())
    print(f"Skrev {OUTPUT_PATH} med {len(set(dates))} händelse(r).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

