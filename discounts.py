from playwright.sync_api import sync_playwright
import pandas as pd
import re
from datetime import datetime
import time

TARGET_BRANDS = [
    "Maruti", "Hyundai", "Tata", "Mahindra", "Kia", "MG",
    "Toyota", "Honda", "Renault", "Nissan", "Skoda", "Volkswagen", "BYD", "Volvo"
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Bengaluru", "Chennai", "Pune", "Hyderabad", "Kolkata",
    "Ahmedabad", "Jaipur", "Chandigarh", "Coimbatore", "Indore", "Bhopal", "Nagpur",
    "Noida", "Gurgaon", "Gurugram", "Faridabad", "Ghaziabad", "Lucknow", "Kanpur", "Surat", "Vadodara"
]

KEYWORDS = ["discount", "offer", "dealer", "price", "booking", "on-road", "quotation"]


class TeamBHPOfferScraper:

    def __init__(self):
        self.results = []

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        self.page = self.context.new_page()

    def get_dealership_threads(self, max_threads=20):
        print("[INFO] Opening Team-BHP homepage first (human behaviour)")
        self.page.goto("https://www.team-bhp.com/", timeout=60000)
        self.page.wait_for_timeout(5000)

        print("[INFO] Opening Indian Car Dealerships forum")
        url = "https://www.team-bhp.com/forum/indian-car-dealerships/"
        self.page.goto(url, timeout=60000)
        self.page.wait_for_timeout(6000)

        rows = self.page.locator("tr.threadbit")
        total = rows.count()
        print(f"[INFO] Total threads found: {total}")

        thread_links = []

        for i in range(min(total, max_threads)):
            row = rows.nth(i)

            try:
                title = row.locator("a.title").inner_text().strip()
                link = row.locator("a.title").get_attribute("href")
            except:
                continue

            title_lower = title.lower()

            if any(k in title_lower for k in KEYWORDS):
                full_link = link if link.startswith("http") else "https://www.team-bhp.com" + link
                thread_links.append((title, full_link))
                print(f"   ✔ Matched Thread: {title}")

        return thread_links

    def scrape_thread(self, title, url):
        print(f"\n[THREAD] {title}")
        self.page.goto(url, timeout=60000)
        self.page.wait_for_timeout(5000)

        try:
            post_block = self.page.locator("div.post_message").first
            post_text = post_block.inner_text().strip()
        except:
            post_text = ""

        full_text = f"{title} {post_text}"

        brand = self.detect_brand(full_text)
        city = self.detect_city(full_text)
        discount = self.detect_discount(full_text)

        if brand or discount or city:
            print(f"   ✔ Brand: {brand} | City: {city} | Discount: {discount}")
            self.results.append({
                "Brand": brand,
                "City": city,
                "Discount": discount,
                "Thread Title": title,
                "Post Text": post_text[:500],
                "URL": url,
                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            print("   ✖ No usable offer data")

        time.sleep(2)  # human-like delay

    def detect_brand(self, text):
        text_lower = text.lower()
        for brand in TARGET_BRANDS:
            if brand.lower() in text_lower:
                return brand
        return None

    def detect_city(self, text):
        text_lower = text.lower()
        for city in CITIES:
            pattern = r"\b" + re.escape(city.lower()) + r"\b"
            if re.search(pattern, text_lower):
                return city
        return None

    def detect_discount(self, text):
        patterns = [
            r"₹\s?\d+[,\d]*",
            r"\d+\s?k",
            r"\d+\s?lakh",
            r"\d+\s?lakhs",
            r"\d+\s?thousand"
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group()
        return None

    def save_to_excel(self):
        if not self.results:
            print("[WARN] No offers found")
            return

        df = pd.DataFrame(self.results)
        file_name = f"team_bhp_offers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"\n[SUCCESS] Data saved to {file_name}")

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def run(self):
        threads = self.get_dealership_threads(max_threads=30)

        for title, link in threads:
            try:
                self.scrape_thread(title, link)
            except Exception as e:
                print(f"[ERROR] Failed thread: {e}")

        self.save_to_excel()
        self.close()


if __name__ == "__main__":
    scraper = TeamBHPOfferScraper()
    scraper.run()
