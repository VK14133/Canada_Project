import pytest
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
import shutil

from compare_file import CompareFile

def test_scrape_links():
    # Create output folder if it doesn't exist
    output_dir = "volunteergreatermoncton"
    os.makedirs(output_dir, exist_ok=True)

    capture_dir = "output"
    os.makedirs(capture_dir, exist_ok=True)

    # Generate timestamped file name
    base_name = os.path.splitext(os.path.basename(__file__))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{base_name}_{timestamp}.txt")

    seen_links = set()   # ✅ keep track of unique links

    scrape_successful = True

    categorys = ["administration","communication","friendly-help","teaching","food-services","transport","housing","other"]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto("https://volunteergreatermoncton.com/opportunities/")
            page.wait_for_timeout(3000)

            with open(output_file, "w") as file:
                for categoty in categorys:
                    page.goto(f"https://volunteergreatermoncton.com/category/{categoty}/")
                    page.wait_for_timeout(3000)

                    volunteer_cards = page.locator(".more-link")

                    count = volunteer_cards.count()
                    for i in range(count):
                        link = volunteer_cards.nth(i).get_attribute("href")
                        if link and link not in seen_links:
                            seen_links.add(link)
                            file.write(f"{link}\n")

            browser.close()

    except Exception as e:
        scrape_successful = False
        print(f"[ERROR] Scraping failed: {e}")

    # 🔁 Use CompareFile after scraping is done
    old_file = "volunteergreatermoncton/volunteergreatermoncton.txt"  # Replace with actual path
    compare_output = os.path.join(capture_dir, f"new_{base_name}_{timestamp}.txt")

    if scrape_successful:
        if os.path.exists(old_file):
            comparator = CompareFile(old_file, output_file, compare_output)
            comparator.get_unique_url()

            # ✅ Backup the old baseline before overwriting
            backup_file = old_file + ".bak"
            shutil.copy(old_file, backup_file)
            print(f"[INFO] Backup created at: {backup_file}")
        else:
            print(f"[INFO] No previous file found at {old_file}. Skipping comparison.")

        # ✅ Overwrite old baseline with new scrape
        shutil.copy(output_file, old_file)
        print(f"[INFO] Baseline updated at: {old_file}")
    else:
        print("[WARNING] Scrape incomplete or failed. Baseline file not updated.")
