import requests
from bs4 import BeautifulSoup
import os
import time

# --- কনফিগারেশন ---
URL = "https://shed.gov.bd/site/view/notices"
TELEGRAM_TOKEN = "8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"  # আপনার বট টোকেন দিন
CHAT_ID = "6382850126"          # আপনার চ্যাট আইডি দিন
TRACK_FILE = "sent_notices.txt"

# পূর্বে পাঠানো নোটিশের তালিকা লোড করা
if os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        sent_notices = set(f.read().splitlines())
else:
    sent_notices = set()

def send_telegram_message(text):
    """টেলিগ্রামে নোটিফিকেশন পাঠানোর ফাংশন"""
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print(f"টেলিগ্রাম মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")

def check_shed_notices():
    global sent_notices
    print("নতুন নোটিশ চেক করা হচ্ছে...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print("ওয়েবসাইটে প্রবেশ করা যাচ্ছে না।")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # SHED ওয়েবসাইটের নোটিশ টেবিল বা লিস্ট সিলেক্ট করা (ওয়েবসাইটের স্ট্রাকচার অনুযায়ী)
        # সাধারণত নোটিশগুলো টেবিলের <tr> বা নির্দিষ্ট ক্লাসে থাকে
        notice_table = soup.find('table', {'id': 'noticeTable'}) or soup.find('div', {'class': 'list-holder'})
        if not notice_table:
            # বিকল্প হিসেবে সব লিংক খোঁজা যদি নির্দিষ্ট টেবিল না পাওয়া যায়
            notice_elements = soup.find_all('a', href=True)
        else:
            notice_elements = notice_table.find_all('a', href=True)

        new_notices_found = []

        for element in notice_elements:
            title = element.text.strip()
            link = element['href']
            
            # লিংক পূর্ণাঙ্গ না হলে ডোমেইন যোগ করা
            if link.startswith('/'):
                link = f"https://shed.gov.bd{link}"
                
            # শুধু নোটিশ লিংক ফিল্টার করার জন্য (যদি লিংকে নির্দিষ্ট প্যাটার্ন থাকে)
            if "site/view/notices" in link or "site/office_order" in link or "/notice/" in link:
                
                # ১. ফিল্টার: "সার্কুলার" বা "Circular" থাকলে বাদ যাবে
                if "circular" in title.lower() or "সার্কুলার" in title:
                    continue
                
                # ২. ফিল্টার: পুরোনো নোটিশ হলে বাদ যাবে
                if link in sent_notices:
                    continue
                    
                new_notices_found.append({"title": title, "link": link})

        # নতুন নোটিশগুলো উল্টো করে (পুরোনো থেকে নতুন) প্রসেস করা যাতে টেলিগ্রামে একদম নতুনটা সবার শেষে আসে
        for notice in reversed(new_notices_found):
            message = f"🔔 *নতুন নোটিশ প্রকাশিত হয়েছে!*\n\n📌 *শিরোনাম:* {notice['title']}\n\n🔗 *লিংক:* {notice['link']}"
            
            # টেলিগ্রামে পাঠানো
            send_telegram_message(message)
            print(f"পাঠানো হয়েছে: {notice['title']}")
            
            # ট্র্যাকিং ফাইলে সেভ করা
            with open(TRACK_FILE, "a", encoding="utf-8") as f:
                f.write(notice['link'] + "\n")
            sent_notices.add(notice['link'])
            
            time.sleep(2) # টেলিগ্রাম স্প্যাম রোধে সামান্য বিরতি

    except Exception as e:
        print(f"ত্রুটি ঘটেছে: {e}")

if __name__ == "__main__":
    # এই ফাংশনটি আপনি ক্রন জব (Cron Job) বা টাস্ক সিডিউলার দিয়ে প্রতি ১০-১৫ মিনিট পর পর চালাতে পারেন
    check_shed_notices()
