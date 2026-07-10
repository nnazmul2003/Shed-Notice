import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SHED_URL = "https://shed.gov.bd/pages/notices"

LAST_FILE = "last_notice.json"

TELEGRAM_TOKEN = os.environ["8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"]
CHAT_ID = os.environ["6382850126"]


def load_last():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )


def get_latest_notice():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(SHED_URL, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    notice = soup.find("a", href=True)

    if notice:
        title = notice.get_text(strip=True)
        link = urljoin(SHED_URL, notice["href"])

        return {
            "title": title,
            "link": link
        }

    return None


def main():

    print("SHED Notice Checker Started")

    last = load_last()

    latest = get_latest_notice()

    if latest:

        if last.get("link") != latest["link"]:

            message = (
                "🔔 নতুন SHED নোটিশ\n\n"
                f"📌 {latest['title']}\n\n"
                f"🔗 {latest['link']}"
            )

            send_telegram(message)

            save_last(latest)

            print("Notification Sent")

        else:
            print("No New Notice")

    else:
        print("Notice not found")


if __name__ == "__main__":
    main()
