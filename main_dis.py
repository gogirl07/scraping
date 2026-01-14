from datetime import datetime
from pathlib import Path
from advertgallery_city_scraper import AdvertGalleryCityScraper


def main():
    print("=== CITY WISE DISCOUNTS / OFFERS SCRAPER (ADVERT GALLERY) STARTED ===")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"city_wise_latest_discounts_{timestamp}.xlsx"

    scraper = AdvertGalleryCityScraper()

    try:
        data = scraper.run_and_get_data()

        if not data:
            print("\n❌ No data collected.")
            return

        import pandas as pd
        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False)

        print(f"\n✅ SUCCESS! File generated: {output_file}")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
