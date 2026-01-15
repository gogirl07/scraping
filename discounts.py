from playwright.sync_api import sync_playwright

import pandas as pd

import time

from datetime import datetime
 
COMPANIES = [

    "Maruti Suzuki", "Hyundai", "Mahindra", "Kia", "MG Motor",

    "Toyota", "Honda", "Renault", "Nissan", "Skoda",

    "Volkswagen", "BYD", "Volvo", "Tata Motors"

]
 
CITIES = [

    "Pune", "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",

    "Ahmedabad", "Jaipur", "Indore", "Bhopal", "Nagpur", "Surat", "Vadodara"

]
 
 
class GoogleSearchOfferScraper:
 
    def __init__(self):

        self.results = []
 
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(

            headless=False,

            args=["--start-maximized"]

        )
 
        self.context = self.browser.new_context(

            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "

                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

            viewport={"width": 1400, "height": 900}

        )
 
        self.page = self.context.new_page()
 
    def search_and_scrape(self, company, city):

        query = f"latest offers on {company} in {city}"

        print(f"\n[SEARCH] {query}")
 
        self.page.goto("https://www.google.com", timeout=60000)

        self.page.wait_for_timeout(3000)
 
        # Accept cookies if present

        try:

            self.page.locator("button:has-text('Accept')").click(timeout=3000)

        except:

            pass
 
        search_box = self.page.locator("input[name='q']")

        search_box.click()

        self.page.wait_for_timeout(500)

        search_box.fill(query)

        self.page.wait_for_timeout(500)

        search_box.press("Enter")
 
        self.page.wait_for_timeout(5000)
 
        results = self.page.locator("div.g")

        count = results.count()

        print(f"[INFO] {count} results found")
 
        for i in range(min(count, 5)):  # top 5 results only

            block = results.nth(i)
 
            try:

                title = block.locator("h3").inner_text()

            except:

                title = ""
 
            try:

                snippet = block.locator("span").inner_text()

            except:

                snippet = ""
 
            try:

                link = block.locator("a").first.get_attribute("href")

            except:

                link = ""
 
            self.results.append({

                "Company": company,

                "City": city,

                "Search Query": query,

                "Title": title,

                "Snippet": snippet,

                "URL": link,

                "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            })
 
        # Human-like delay

        time.sleep(5)
 
    def save_to_excel(self):

        df = pd.DataFrame(self.results)

        file_name = f"google_search_offers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        df.to_excel(file_name, index=False)

        print(f"\n[SUCCESS] Data saved to {file_name}")
 
    def close(self):

        self.context.close()

        self.browser.close()

        self.playwright.stop()
 
    def run(self):

        for company in COMPANIES:

            for city in CITIES:

                try:

                    self.search_and_scrape(company, city)

                except Exception as e:

                    print(f"[ERROR] {company} - {city} : {e}")

                    continue
 
        self.save_to_excel()

        self.close()
 
 
if __name__ == "__main__":

    scraper = GoogleSearchOfferScraper()

    scraper.run()

 