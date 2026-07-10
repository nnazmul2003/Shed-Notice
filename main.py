import os
import json
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin


SITES = {
    "SHED": "https://shed.gov.bd/pages/notification-circulars",
}


BOT_TOKEN = "8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"
CHAT_ID = "6382850126"

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



def extract_date(text):

    dates = re.findall(
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        text
    )

    for d in dates:

        try:
            return datetime.strptime(
                d.replace("/", "-"),
                "%d-%m-%Y"
            )

        except:
            pass

    return None



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


    notices = []


    for row in soup.find_all("tr"):

        link = row.find(
            "a",
            href=True
        )


        if not link:
            continue


        href = link["href"]


        if ".pdf" not in href.lower():
            continue


        text = row.get_text(
            " ",
            strip=True
        )


        lower = text.lower()


        # Circular বাদ
        bad = [
            "circular",
            "notification",
            "পরিপত্র"
        ]


        if any(
            x in lower
            for x in bad
        ):
            continue



        date = extract_date(text)


        if date is None:
            continue



        notices.append({

            "title": text,

            "link": urljoin(
                url,
                href
            ),

            "date": date

        })



    # fallback
    if not notices:

        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a["href"]


            if ".pdf" not in href.lower():
                continue


            title = a.get_text(
                " ",
                strip=True
            )


            lower = title.lower()


            if "circular" in lower:
                continue


            date = extract_date(title)


            if date:

                notices.append({

                    "title": title,

                    "link": urljoin(
                        url,
                        href
                    ),

                    "date": date

                })



    if not notices:
        return None



    notices.sort(
        key=lambda x:x["date"],
        reverse=True
    )


    newest = notices[0]


    return {

        "title": newest["title"],

        "link": newest["link"]

    }




def main():

    print(
        "SHED Notice Checker Started"
    )


    last = load()


    for name,url in SITES.items():

        notice = latest(url)


        if notice is None:

            print(
                "No Notice Found"
            )

            continue



        if last.get(name) != notice["link"]:


            message = (
                f"🔔 New Notice ({name})\n\n"
                f"📌 {notice['title']}\n\n"
                f"🔗 {notice['link']}"
            )


            telegram(message)


            last[name] = notice["link"]


            print(
                "Telegram Sent"
            )


        else:

            print(
                "No New Notice"
            )



    save(last)



if __name__ == "__main__":
    main()
