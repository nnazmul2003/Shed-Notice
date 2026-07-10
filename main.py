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

        with open(
            LAST,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    return {}



def save(data):

    with open(
        LAST,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )



def telegram(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )


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


    notices = []


    # Table থেকে Notice খোঁজা
    for row in soup.find_all("tr"):


        link = row.find(
            "a",
            href=True
        )


        if not link:
            continue


        href = link["href"]


        title = row.get_text(
            " ",
            strip=True
        )


        if ".pdf" not in href.lower():
            continue


        text = title.lower()


        # Circular বাদ
        if "circular" in text:
            continue


        # Notice ছাড়া বাদ
        if "notice" not in text:
            continue



        # তারিখ খোঁজা
        dates = re.findall(
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            title
        )


        if not dates:
            continue



        try:

            date = datetime.strptime(
                dates[0].replace("/", "-"),
                "%d-%m-%Y"
            )


        except:

            continue



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



    # নতুন তারিখ আগে
    notices.sort(
        key=lambda x: x["date"],
        reverse=True
    )


    notice = notices[0]


    return {

        "title": notice["title"],

        "link": notice["link"]

    }



def main():


    print(
        "SHED Notice Checker Started"
    )


    last = load()



    for name, url in SITES.items():


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
