import requests
from bs4 import BeautifulSoup
import os

# --- কনফিগারেশন ---
URL = "https://shed.gov.bd/site/view/notices"
TELEGRAM_TOKEN = "8735006573:AAGacSF8BTuTPvVpO9P2hmOqos93XBzH3GY"  # আপনার বটের টোকেন দিন
CHAT_ID = "6382850126"          # আপনার চ্যাট আইডি দিন
TRACK_FILE = "sent_notices.txt"

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
    print("🔄 ওয়েবসাইটের সবচেয়ে সাম্প্রতিক নোটিশটি চেক করা হচ্ছে...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print("❌ ওয়েবসাইটে প্রবেশ করা যাচ্ছে না।")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # নোটিশ টেবিলের সব রো (Rows) খোঁজা
        # সরকারি ওয়েবসাইটের নোটিশ সাধারণত টেবিলের ভেতরে থাকে
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            
            # প্রথম row-তে সাধারণত হেডার থাকে, তাই পরের রোগুলো চেক করা
            for row in rows:
                link_element = row.find('a', href=True)
                if link_element:
                    title = link_element.text.strip()
                    link = link_element['href']
                    
                    if link.startswith('/'):
                        link = f"https://shed.gov.bd{link}"
                        
                    # ফিল্টার: সার্কুলার হলে বাদ যাবে
                    if "circular" in title.lower() or "সার্কুলার" in title:
                        continue # পরের রো-তে চলে যাবে
                        
                    # ফিল্টার: অলরেডি পাঠানো হয়ে থাকলে বাদ
                    if link in sent_notices:
                        print("ℹ️ সবচেয়ে সাম্প্রতিক নোটিশটি ইতিমধ্যে পাঠানো হয়েছে। নতুন কোনো নোটিশ নেই।")
                        return
                    
                    # নোটিশের তারিখ খোঁজা (যদি টেবিলে আলাদা কলামে থাকে)
                    date_text = ""
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        # সাধারণত শেষ বা মাঝের কোনো কলামে তারিখ থাকে
                        for cell in cells:
                            if "-" in cell.text or "/" in cell.text: # তারিখের ফরম্যাট চেক
                                date_text = cell.text.strip()
                    
                    # টেলিগ্রাম মেসেজ ফরম্যাট
                    date_info = f"📅 *তারিখ:* {date_text}\n" if date_text else ""
                    message = f"🔔 *নতুন সাম্প্রতিক নোটিশ!*\n\n📌 *শিরোনাম:* {title}\n{date_info}\n🔗 *লিংক:* {link}"
                    
                    # পাঠানো
                    send_telegram_message(message)
                    print(f"✅ টেলিগ্রামে পাঠানো হয়েছে: {title}")
                    
                    # ট্র্যাকিং ফাইলে সেভ
                    with open(TRACK_FILE, "a", encoding="utf-8") as f:
                        f.write(link + "\n")
                    
                    # শুধু সবচেয়ে রিসেন্ট একটা নোটিশ প্রসেস করেই লুপ থামিয়ে দেওয়া
                    return 
        else:
            print("❌ নোটিশ টেবিলটি খুঁজে পাওয়া যায়নি।")
            
    except Exception as e:
        print(f"❌ ত্রুটি: {e}")

if __name__ == "__main__":
    check_recent_notice()
