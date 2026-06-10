import requests
import json
import base64
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

DEFAULT_IMAGE = "https://raw.githubusercontent.com/SNLry/events-test/main/default_kuva.png"


# 🔑 TOKEN
def get_token():
    url = "https://www.suomisport.fi/oauth2/token"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        print("Token error:", response.status_code, response.text)
        return None

    return response.json().get("access_token")


# 📅 muotoilut
def format_date_range(start, end):
    if not start:
        return ""

    s = datetime.fromisoformat(start.replace("Z", "+00:00"))

    if not end:
        return s.strftime("%d.%m.%Y")

    e = datetime.fromisoformat(end.replace("Z", "+00:00"))

    if s.date() == e.date():
        return s.strftime("%d.%m.%Y")

    return f"{s.strftime('%d.%m.%Y')} - {e.strftime('%d.%m.%Y')}"


def format_price(cents):
    if not cents:
        return "Ilmainen"
    return f"{cents/100:.2f} €"


# ✅ EI kosketa URLiin!
def get_image_tag(url, size=150):
    if not url:
        url = DEFAULT_IMAGE

    return f'<img src="{url}" style="width:{size}px; border-radius:6px;" />'


# ✅ tulevat
def get_future_events(events):
    now = datetime.now(timezone.utc)

    return [
        e for e in events
        if e.get("startDateTime") and
        datetime.fromisoformat(
            e["startDateTime"].replace("Z", "+00:00")
        ) >= now
    ]


# 🌐 ALL EVENTS (kaikki, uusin ensin)
def generate_all_events_html(events):


    now = datetime.now(timezone.utc)

    # ✅ SUODATA vain nykyiset ja tulevat
    filtered_events = [
        e for e in events
        if e.get("startDateTime") and
        datetime.fromisoformat(
            e["startDateTime"].replace("Z", "+00:00")
        ) >= now
    ]

    # ✅ JÄRJESTÄ vanhimmasta uusimpaan
    events_sorted = sorted(
        filtered_events,
        key=lambda e: e.get("startDateTime", "")
    )


    html = """
<html>
<head>
<meta charset="UTF-8">
<style>
body { font-family: Arial; max-width: 900px; margin: auto; }

.event {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #ddd;
    padding: 15px 0;
    gap: 20px;
}

.button {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 14px;
    background-color: #1e73be;   /* sininen */
    color: white;
    text-decoration: none;
    border-radius: 20px;         /* pyöristetty */
    font-size: 14px;
    font-weight: 500;
    transition: 0.2s;
}

.button:hover {
    background-color: #155a96;
    transform: translateY(-1px);
}
.text { flex: 1; }

</style>
</head>
<body>
<h1>Tulevat tapahtumat</h1>
"""

    for ev in events_sorted:

        img = get_image_tag(ev.get("imageUrl"), size=300)
        link = get_event_url(ev)

        html += f"""
<div class="event">
    <div class="text">
        <h2>{ev.get('name','')}</h2>
        <p>{format_date_range(ev.get('startDateTime'), ev.get('endDateTime'))}</p>
        <p>{ev.get('locationDescription','')}</p>
        <p>{ev.get('locationAddress','')}</p>
        <p><strong>{format_price(ev.get('priceInCents'))}</strong></p>
        <a href="{link}" target="_blank" class="button">Ilmoittaudu →</a>
    </div>
    <div>
        {img}
    </div>
</div>
"""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    html += f"""
    <p style="font-size:12px;color:#999;text-align:center;margin-top:30px;">
            🕒 Päivitetty: {timestamp}
    </p>

    """
    html += "</body></html>"

    with open("events_all.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ events_all.html valmis")


# 🌐 FRONT (3 seuraavaa)
def generate_frontpage_html(events):

    future = get_future_events(events)

    events_sorted = sorted(
        future,
        key=lambda e: e.get("startDateTime", "")
    )

    next_events = events_sorted[:3]

    html = """
<html>
<head>
<meta charset="UTF-8">
<style>
body { font-family: Arial; }

.event {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px solid #ddd;
    padding: 10px 0;
    gap: 15px;
}
.button {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 14px;
    background-color: #1e73be;   /* sininen */
    color: white;
    text-decoration: none;
    border-radius: 20px;         /* pyöristetty */
    font-size: 14px;
    font-weight: 500;
    transition: 0.2s;
}
.all-events-button {
    display: block;
    margin: 30px auto 10px auto;
    padding: 12px 20px;
    background-color: #1e73be;
    color: white;
    text-align: center;
    text-decoration: none;
    border-radius: 25px;
    font-size: 16px;
    font-weight: 600;
    width: fit-content;
    transition: 0.2s;
}

.all-events-button:hover {
    background-color: #155a96;
    transform: translateY(-1px);
}


.button:hover {
    background-color: #155a96;
    transform: translateY(-1px);
}
.text { flex: 1; }

</style>
</head>
<body>
"""

    for ev in next_events:

        img = get_image_tag(ev.get("imageUrl"), size=250)
        link = get_event_url(ev)

        html += f"""
<div class="event">
    <div class="text">
        <h3>{ev.get('name','')}</h3>
        <p>{format_date_range(ev.get('startDateTime'), ev.get('endDateTime'))}</p>
        <p>{ev.get('locationDescription','')}</p>
        <p><strong>{format_price(ev.get('priceInCents'))}</strong></p>
        <a href="{link}" target="_blank" class="button">Ilmoittaudu →</a>
    </div>
    <div>
        {img}
    </div>
</div>
"""

    html += """
    <a href="https://www.nyrkkeilyliitto.com/tapahtumakalenteri/" class="all-events-button">Katso kaikki tapahtumat →</a>
</body>
</html>
"""

    with open("events_front.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ events_front.html valmis")


def get_event_url(ev):
    uuid = ev.get("uuid")
    if not uuid:
        return "#"
    return f"https://www.suomisport.fi/events/{uuid}"

# 🚀 MAIN
def main():
    token = get_token()

    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "https://www.suomisport.fi/api/public/v2/event/list"

    all_events = []
    seen_ids = set()
    page = 0

    while True:

        response = requests.post(
            f"{url}?page={page}&size=100",  # ✅ tässä ei saa olla &amp;
            headers=headers,
            json={
                "organizerId": 5472,
                "eventVisibility": "PUBLIC",
                "dateRange": {"start": "2010-01-01T00:00:00.000Z"}
            }
        )

        print(f"Page {page} STATUS:", response.status_code)

        if response.status_code != 200:
            print(response.text)
            break

        data = response.json()
        items = data.get("content", [])
        total = data.get("pageable", {}).get("total", 0)

        if not items:
            break

        for item in items:
            eid = item.get("eventId")

            if eid not in seen_ids:
                seen_ids.add(eid)
                all_events.append(item)

        if len(all_events) >= total:
            break

        page += 1

    print("EVENTS:", len(all_events))

    with open("events_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)

    generate_all_events_html(all_events)
    generate_frontpage_html(all_events)


if __name__ == "__main__":
    main()