import requests
from icalendar import Calendar
import hashlib
import time
import os

ICS_URL = "https://wmsu.edu.ph/events/?ical=1"
CACHE_FILE = "events_hash.txt"
POLL_INTERVAL = 600  # seconds (10 minutes)

def fetch_ics():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    }
    r = requests.get(ICS_URL, headers=headers)
    r.raise_for_status()
    return r.content

def get_hash(data):
    return hashlib.sha256(data).hexdigest()

def parse_events(data):
    cal = Calendar.from_ical(data)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            title = str(component.get("SUMMARY"))
            start = component.get("DTSTART").dt
            end = component.get("DTEND").dt
            events.append((title, start, end))
    return events

def main():
    print("🔄 Starting WMSU event watcher...")

    while True:
        try:
            data = fetch_ics()
            new_hash = get_hash(data)

            # Load old hash if exists
            old_hash = None
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    old_hash = f.read().strip()

            if new_hash != old_hash:
                print("📢 Calendar UPDATED!")

                # Save new hash
                with open(CACHE_FILE, "w") as f:
                    f.write(new_hash)

                # Parse and show events
                events = parse_events(data)
                for title, start, end in events[:5]:  # limit to 5 events
                    print(f"📌 {title}")
                    print(f"   📅 {start} → {end}\n")
            else:
                print("✅ No changes detected.")

        except Exception as e:
            print("❌ Error:", e)

        print(f"⏳ Waiting {POLL_INTERVAL/60} minutes...\n")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
