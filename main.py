import requests
from bs4 import BeautifulSoup
import os
import time

# --- কনফিগারেশন ---
URL = "https://shed.gov.bd/site/view/notices"
TELEGRAM_TOKEN = "8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"  # আপনার বটের টোকেন দিন
CHAT_ID = "6382850126"          # আপনার চ্যাট আইডি দিন
TRACK_FILE = "sent_notices.txt"
CHECK_INTERVAL = 120                       # 👈 ২ মিনিট (১২০ সেকেন্ড) পর পর চেক করবে

if os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "r", encoding="utf-8") as f:
        sent_notices = set(f.read().splitlines())
else:
    sent_notices = set()

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print(f"❌ টেলিগ্রাম এরর: {e}")

def check_recent_notice():
    global sent_notices
    print(f"🔄 [{time.strftime('%H:%M:%S')}] ওয়েবসাইটের নোটিশ চেক করা হচ্ছে...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print("❌ ওয়েবসাইটে প্রবেশ করা যাচ্ছে না।")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')
            new_count = 0
            
            for row in rows:
                link_element = row.find('a', href=True)
                if link_element:
                    title = link_element.text.strip()
                    link = link_element['href']
                    
                    if link.startswith('/'):
                        link = f"https://shed.gov.bd{link}"
                        
                    if "circular" in title.lower() or "সার্কুলার" in title:
                        continue
                        
                    # যদি নোটিশটি অলরেডি পাঠানো হয়ে থাকে, তবে লুপ ব্রেক করবে (কারণ এর পরেরগুলো আরও পুরোনো)
                    if link in sent_notices:
                        break
                    
                    # নতুন নোটিশ পাওয়া গেছে!
                    message = f"🔔 *নতুন নোটিশ প্রকাশিত হয়েছে!*\n\n📌 *শিরোনাম:* {title}\n\n🔗 *লিংক:* {link}"
                    send_telegram_message(message)
                    print(f"✅ টেলিগ্রামে পাঠানো হয়েছে: {title}")
                    
                    with open(TRACK_FILE, "a", encoding="utf-8") as f:
                        f.write(link + "\n")
                    sent_notices.add(link)
                    new_count += 1
                    
                    time.sleep(2) # সামান্য বিরতি
            
            if new_count == 0:
                print("ℹ️ নতুন কোনো নোটিশ পাওয়া যায়নি।")
        else:
            print("❌ নোটিশ টেবিলটি খুঁজে পাওয়া যায়নি।")
            
    except Exception as e:
        print(f"❌ ত্রুটি: {e}")

if __name__ == "__main__":
    print("🚀 নোটিশ মনিটর चालू করা হয়েছে (প্রতি ২ মিনিট পর পর চেক করবে)...")
    while True:
        check_recent_notice()
        time.sleep(CHECK_INTERVAL) # ২ মিনিট অপেক্ষা করবে
