import asyncio
import aiohttp
import re
import html  # এই লাইব্রেরিটা অ্যাড করা হয়েছে SMS এর এরর সলভ করার জন্য
from collections import deque
import logging

# লগিং সেটআপ 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# ================= কনফিগারেশন =================
API_KEY = "nxa_99f2f67b13e0e02bca175b1cbc40d57128958702"
BOT_TOKEN = "8647348457:AAEi5Kre2Df4Xeig80aZzsd_7zR9MFO739Y"
CHAT_ID = "-1003800508577"
API_LOGS_URL = "http://2.58.82.137:5000/api/v1/console/logs?limit=200"
# ==========================================================

# কান্ট্রি কোড লিস্ট
COUNTRY_CODES = {
    "1": ("US", "🇺🇸"), "7": ("RU", "🇷🇺"), "20": ("EG", "🇪🇬"), "27": ("ZA", "🇿🇦"),
    "30": ("GR", "🇬🇷"), "31": ("NL", "🇳🇱"), "32": ("BE", "🇧🇪"), "33": ("FR", "🇫🇷"),
    "34": ("ES", "🇪🇸"), "36": ("HU", "🇭🇺"), "39": ("IT", "🇮🇹"), "40": ("RO", "🇷🇴"),
    "41": ("CH", "🇨🇭"), "43": ("AT", "🇦🇹"), "44": ("GB", "🇬🇧"), "45": ("DK", "🇩🇰"),
    "46": ("SE", "🇸🇪"), "47": ("NO", "🇳🇴"), "48": ("PL", "🇵🇱"), "49": ("DE", "🇩🇪"),
    "51": ("PE", "🇵🇪"), "52": ("MX", "🇲🇽"), "53": ("CU", "🇨🇺"), "54": ("AR", "🇦🇷"),
    "55": ("BR", "🇧🇷"), "56": ("CL", "🇨🇱"), "57": ("CO", "🇨🇴"), "58": ("VE", "🇻🇪"),
    "60": ("MY", "🇲🇾"), "61": ("AU", "🇦🇺"), "62": ("ID", "🇮🇩"), "63": ("PH", "🇵🇭"),
    "64": ("NZ", "🇳🇿"), "65": ("SG", "🇸🇬"), "66": ("TH", "🇹🇭"), "81": ("JP", "🇯🇵"),
    "82": ("KR", "🇰🇷"), "84": ("VN", "🇻🇳"), "86": ("CN", "🇨🇳"), "90": ("TR", "🇹🇷"),
    "91": ("IN", "🇮🇳"), "92": ("PK", "🇵🇰"), "93": ("AF", "🇦🇫"), "94": ("LK", "🇱🇰"),
    "95": ("MM", "🇲🇲"), "98": ("IR", "🇮🇷"), "211": ("SS", "🇸🇸"), "212": ("MA", "🇲🇦"),
    "213": ("DZ", "🇩🇿"), "216": ("TN", "🇹🇳"), "218": ("LY", "🇱🇾"), "220": ("GM", "🇬🇲"),
    "221": ("SN", "🇸🇳"), "222": ("MR", "🇲🇷"), "223": ("ML", "🇲🇱"), "224": ("GN", "🇬🇳"),
    "225": ("CI", "🇨🇮"), "226": ("BF", "🇧🇫"), "227": ("NE", "🇳🇪"), "228": ("TG", "🇹🇬"),
    "229": ("BJ", "🇧🇯"), "230": ("MU", "🇲🇺"), "231": ("LR", "🇱🇷"), "232": ("SL", "🇸🇱"),
    "233": ("GH", "🇬🇭"), "234": ("NG", "🇳🇬"), "235": ("TD", "🇹🇩"), "236": ("CF", "🇨🇫"),
    "237": ("CM", "🇨🇲"), "238": ("CV", "🇨🇻"), "239": ("ST", "🇸🇹"), "240": ("GQ", "🇬🇶"),
    "241": ("GA", "🇬🇦"), "242": ("CG", "🇨🇬"), "243": ("CD", "🇨🇩"), "244": ("AO", "🇦🇴"),
    "245": ("GW", "🇬🇼"), "246": ("IO", "🇮🇴"), "247": ("AC", "🇦🇨"), "248": ("SC", "🇸🇨"),
    "249": ("SD", "🇸🇩"), "250": ("RW", "🇷🇼"), "251": ("ET", "🇪🇹"), "252": ("SO", "🇸🇴"),
    "253": ("DJ", "🇩🇯"), "254": ("KE", "🇰🇪"), "255": ("TZ", "🇹🇿"), "256": ("UG", "🇺🇬"),
    "257": ("BI", "🇧🇮"), "258": ("MZ", "🇲🇿"), "260": ("ZM", "🇿🇲"), "261": ("MG", "🇲🇬"),
    "262": ("RE", "🇷🇪"), "263": ("ZW", "🇿🇼"), "264": ("NA", "🇳🇦"), "265": ("MW", "🇲🇼"),
    "266": ("LS", "🇱🇸"), "267": ("BW", "🇧🇼"), "268": ("SZ", "🇸🇿"), "269": ("KM", "🇰🇲"),
    "290": ("SH", "🇸🇭"), "291": ("ER", "🇪🇷"), "297": ("AW", "🇦🇼"), "298": ("FO", "🇫🇴"),
    "299": ("GL", "🇬🇱"), "350": ("GI", "🇬🇮"), "351": ("PT", "🇵🇹"), "352": ("LU", "🇱🇺"),
    "353": ("IE", "🇮🇪"), "354": ("IS", "🇮🇸"), "355": ("AL", "🇦🇱"), "356": ("MT", "🇲🇹"),
    "357": ("CY", "🇨🇾"), "358": ("FI", "🇫🇮"), "359": ("BG", "🇧🇬"), "370": ("LT", "🇱🇹"),
    "371": ("LV", "🇱🇻"), "372": ("EE", "🇪🇪"), "373": ("MD", "🇲🇩"), "374": ("AM", "🇦🇲"),
    "375": ("BY", "🇧🇾"), "376": ("AD", "🇦🇩"), "377": ("MC", "🇲🇨"), "378": ("SM", "🇸🇲"),
    "379": ("VA", "🇻🇦"), "380": ("UA", "🇺🇦"), "381": ("RS", "🇷🇸"), "382": ("ME", "🇲🇪"),
    "385": ("HR", "🇭🇷"), "386": ("SI", "🇸🇮"), "387": ("BA", "🇧🇦"), "389": ("MK", "🇲🇰"),
    "420": ("CZ", "🇨🇿"), "421": ("SK", "🇸🇰"), "423": ("LI", "🇱🇮"), "500": ("FK", "🇫🇰"),
    "501": ("BZ", "🇧🇿"), "502": ("GT", "🇬🇹"), "503": ("SV", "🇸🇻"), "504": ("HN", "🇭🇳"),
    "505": ("NI", "🇳🇮"), "506": ("CR", "🇨🇷"), "507": ("PA", "🇵🇦"), "508": ("PM", "🇵🇲"),
    "509": ("HT", "🇭🇹"), "590": ("GP", "🇬🇵"), "591": ("BO", "🇧🇴"), "592": ("GY", "🇬🇾"),
    "593": ("EC", "🇪🇨"), "594": ("GF", "🇬🇫"), "595": ("PY", "🇵🇾"), "596": ("MQ", "🇲🇶"),
    "597": ("SR", "🇸🇷"), "598": ("UY", "🇺🇾"), "599": ("CW", "🇨🇼"), "670": ("TL", "🇹🇱"),
    "672": ("NF", "🇳🇫"), "673": ("BN", "🇧🇳"), "674": ("NR", "🇳🇷"), "675": ("PG", "🇵🇬"),
    "676": ("TO", "🇹🇴"), "677": ("SB", "🇸🇧"), "678": ("VU", "🇻🇺"), "679": ("FJ", "🇫🇯"),
    "680": ("PW", "🇵🇼"), "681": ("WF", "🇼🇫"), "682": ("CK", "🇨🇰"), "683": ("NU", "🇳🇺"),
    "685": ("WS", "🇼🇸"), "686": ("KI", "🇰🇮"), "687": ("NC", "🇳🇨"), "688": ("TV", "🇹🇻"),
    "689": ("PF", "🇵🇫"), "690": ("TK", "🇹🇰"), "691": ("FM", "🇫🇲"), "692": ("MH", "🇲🇭"),
    "850": ("KP", "🇰🇵"), "852": ("HK", "🇭🇰"), "853": ("MO", "🇲🇴"), "855": ("KH", "🇰🇭"),
    "856": ("LA", "🇱🇦"), "880": ("BD", "🇧🇩"), "886": ("TW", "🇹🇼"), "960": ("MV", "🇲🇻"),
    "961": ("LB", "🇱🇧"), "962": ("JO", "🇯🇴"), "963": ("SY", "🇸🇾"), "964": ("IQ", "🇮🇶"),
    "965": ("KW", "🇰🇼"), "966": ("SA", "🇸🇦"), "967": ("YE", "🇾🇪"), "968": ("OM", "🇴🇲"),
    "970": ("PS", "🇵🇸"), "971": ("AE", "🇦🇪"), "972": ("IL", "🇮🇱"), "973": ("BH", "🇧🇭"),
    "974": ("QA", "🇶🇦"), "975": ("BT", "🇧🇹"), "976": ("MN", "🇲🇳"), "977": ("NP", "🇳🇵"),
    "992": ("TJ", "🇹🇯"), "993": ("TM", "🇹🇲"), "994": ("AZ", "🇦🇿"), "995": ("GE", "🇬🇪"),
    "996": ("KG", "🇰🇬"), "998": ("UZ", "🇺🇿"),
}

seen_ids = deque(maxlen=5000)
message_queue = asyncio.Queue()  

def get_country_info(number: str):
    num_clean = str(number).replace("+", "").replace("X", "").strip()
    for prefix in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
        if num_clean.startswith(prefix):
            code, flag = COUNTRY_CODES[prefix]
            return f"{flag} {code}"
    return "🌍 GLOBAL"

def format_range(number: str) -> str:
    num_clean = str(number).replace("+", "").strip().upper().replace("X", "")
    if len(num_clean) > 3:
        return f"{num_clean[:-3]}XXX"
    return f"{num_clean}XXX"

def get_otp_digits(sms: str) -> str:
    matches = re.findall(r'\b\d{4,10}\b', str(sms))
    if matches:
        return f"{len(matches[0])}-Digit OTP"
    return "OTP Received"

async def send_to_telegram(session: aiohttp.ClientSession, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        async with session.post(url, json=payload, timeout=5) as resp:
            result = await resp.json()
            if not result.get("ok"):
                logging.error(f"❌ টেলিগ্রাম API এরর: {result.get('description')}")
                return False
            return True
    except Exception as e:
        logging.error(f"❌ টেলিগ্রামে পাঠাতে সমস্যা: {e}")
        return False

async def log_producer(session: aiohttp.ClientSession):
    headers = {"X-API-Key": API_KEY}
    while True:
        try:
            async with session.get(API_LOGS_URL, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data and isinstance(data["data"], list):
                        logs = data["data"]
                        for log in reversed(logs):
                            log_id = log.get("id")
                            
                            if log_id and log_id not in seen_ids:
                                seen_ids.append(log_id)
                                
                                app_name = log.get("app_name", "Unknown").capitalize()
                                number = log.get("number", "")
                                sms_text = log.get("sms", "")
                                
                                if number:
                                    range_val = format_range(number)
                                    country_info = get_country_info(number)
                                    otp_info = get_otp_digits(sms_text)
                                    
                                    # 🔥 ম্যাজিক এখানে: html.escape() করে SMS কে সেফ করা হয়েছে
                                    safe_sms_text = html.escape(sms_text)
                                    safe_app_name = html.escape(app_name)
                                    
                                    msg = (
                                        f"🟢 <b>LIVE WORKING RANGE</b>\n\n"
                                        f"🏳️ <b>Country:</b> {country_info}\n"
                                        f"🌍 <b>Range:</b> <code>{range_val}</code>\n"
                                        f"📱 <b>App:</b> {safe_app_name}\n"
                                        f"🔢 <b>Status:</b> {otp_info}\n\n"
                                        f"✉️ <b>Message:</b>\n"
                                        f"<blockquote><i>{safe_sms_text}</i></blockquote>"
                                    )
                                    
                                    await message_queue.put((range_val, app_name, msg))
        except Exception:
            pass
        await asyncio.sleep(5)

async def message_consumer(session: aiohttp.ClientSession):
    while True:
        range_val, app_name, msg = await message_queue.get()
        
        success = await send_to_telegram(session, msg)
        if success:
            logging.info(f"✅ রেঞ্জ পাঠানো হয়েছে: {range_val} ({app_name}) | লাইনে আরও আছে: {message_queue.qsize()} টি")
        else:
            logging.warning(f"⚠️ গ্রুপে মেসেজ যায়নি! HTML পার্সিং ফিক্স করা হয়েছে।")
            
        message_queue.task_done()
        await asyncio.sleep(10)

async def start_bot():
    logging.info("🚀 Smart Range Forwarder (Bug Fixed) চালু হলো...")
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        task1 = asyncio.create_task(log_producer(session))
        task2 = asyncio.create_task(message_consumer(session))
        
        await asyncio.gather(task1, task2)

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n🛑 স্ক্রিপ্ট বন্ধ করা হয়েছে।")
