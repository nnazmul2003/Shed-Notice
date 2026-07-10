import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


SITES = {
    "SHED": "https://shed.gov.bd/pages/notification-circulars",
}


BOT_TOKEN = ["8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"]
CHAT_ID = ["6382850126"]

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
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    print(response.text)


def latest(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    # সব PDF লিংক খুঁজবে
    for a in soup.find_all("a", href=True):

        href = a["href"]

        title = a.get_text(
            " ",
            strip=True
        )


        if ".pdf" in href.lower():

            pdf = urljoin(
                url,
                href
            )

            if not title:
                title = "SHED নতুন নোটিশ"

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



        old = last.get(name)


        if old != notice["link"]:


            msg = (
                f"🔔 নতুন নোটিশ ({name})\n\n"
                f"📌 {notice['title']}\n\n"
                f"🔗 {notice['link']}"
            )


            telegram(msg)


            last[name] = notice["link"]

            print("Telegram Sent")


        else:

            print("No New Notice")


    save(last)



if __name__ == "__main__":
    main()
