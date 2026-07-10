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



def get_date(text):

    dates = re.findall(
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
        text
    )

    if not dates:
        return None


    try:

        return datetime.strptime(
            dates[0].replace("/", "-"),
            "%d-%m-%Y"
        )

    except:

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


        title = row.get_text(
            " ",
            strip=True
        )


        text = title.lower()



        # শুধুমাত্র Notice
        if (
            "notice" not in text
            and
            "নোটিশ" not in text
        ):
            continue



        # Circular/Notification বাদ
        bad_words = [
            "circular",
            "notification",
            "পরিপত্র",
            "বিজ্ঞপ্তি"
        ]


        if any(
            word in text
            for word in bad_words
        ):
            continue



        date = get_date(title)


        if not date:
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



        if not notice:

            print(
                "No Notice Found"
            )

            continue



        if last.get(name) != notice["link"]:


            msg = (

                f"🔔 New Notice ({name})\n\n"

                f"📌 {notice['title']}\n\n"

                f"🔗 {notice['link']}"

            )


            telegram(msg)


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
