import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


SITES = {
    "SHED": "https://shed.gov.bd/pages/notification-circulars",
}


BOT_TOKEN ="8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"]
CHAT_ID =["6382850126"]

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

    r = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    print(r.json())



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


    # Notice list থেকে প্রথম PDF খোঁজা
    for row in soup.find_all("tr"):

        link = row.find("a", href=True)

        if not link:
            continue


        title = row.get_text(
            " ",
            strip=True
        )


        href = link["href"]


        # Circular বাদ
        if "circular" in title.lower():
            continue


        if ".pdf" in href.lower():

            return {
                "title": title,
                "link": urljoin(url, href)
            }


    # fallback: যদি table না থাকে
    for link in soup.find_all("a", href=True):

        href = link["href"]

        title = link.get_text(
            " ",
            strip=True
        )


        if ".pdf" in href.lower():

            if "circular" in title.lower():
                continue

            return {
                "title": title or "SHED Notice",
                "link": urljoin(url, href)
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



        if last.get(name) != notice["link"]:


            message = (
                f"🔔 নতুন Notice ({name})\n\n"
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
