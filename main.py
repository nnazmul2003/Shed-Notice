import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SITES = {
    "SHED": "https://shed.gov.bd/pages/notification-circulars",
}

BOT_TOKEN = os.environ["8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"]
CHAT_ID = os.environ["6382850126"]

LAST = "last_notice.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def load():
    if os.path.exists(LAST):
        with open(LAST, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save(data):
    with open(LAST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


def latest(url):
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")

    if table is None:
        return None

    for row in table.find_all("tr"):

        link = row.find("a", href=True)

        if not link:
            continue

        title = link.get_text(" ", strip=True)

        if not title:
            continue

        pdf = urljoin(url, link["href"])

        return {
            "title": title,
            "link": pdf
        }

    return None


def main():

    print("SHED Notice Checker Started")

    last = load()

    for name, url in SITES.items():

        notice = latest(url)

        if notice is None:
            print("Notice not found")
            continue

        old_link = last.get(name)

        if old_link != notice["link"]:

            message = (
                f"🔔 নতুন নোটিশ ({name})\n\n"
                f"📌 {notice['title']}\n\n"
                f"🔗 {notice['link']}"
            )

            telegram(message)

            last[name] = notice["link"]

            print("Telegram Sent")

        else:
            print("No New Notice")

    save(last)


if __name__ == "__main__":
    main()
