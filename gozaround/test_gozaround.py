import pytest
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from compare_file import CompareFile
import shutil

def test_scrape_links():
    output_dir = "gozaround"
    os.makedirs(output_dir, exist_ok=True)

    capture_dir = "output"
    os.makedirs(capture_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(__file__))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{base_name}_{timestamp}.txt")

    seen_links = set()   # ✅ keep track of unique links

    scrape_successful = True

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://www.gozaround.com/browse")
            page.wait_for_timeout(3000)

            prev_height = 0
            same_height_count = 0

            with open(output_file, "w") as file:
                while True:
                    # Scroll to bottom
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    page.wait_for_timeout(5000)

                    # Check new height
                    new_height = page.evaluate("document.body.scrollHeight")

                    if new_height == prev_height:
                        same_height_count += 1
                        if same_height_count > 2:
                            print("[INFO] No more content to load. Exiting scroll.")
                            break
                    else:
                        same_height_count = 0
                        prev_height = new_height

                # Once scrolling is done, collect all cards
                volunteer_cards = page.locator(".text-dark.font-weight-bold.stretched-link")
                total = volunteer_cards.count()
                print(f"[INFO] Found {total} volunteer links.")

                for i in range(total):
                    link = volunteer_cards.nth(i).get_attribute("href")
                    if link and link not in seen_links:
                        seen_links.add(link)
                        file.write(f"{link}\n")

            browser.close()

    except Exception as e:
        scrape_successful = False
        print(f"[ERROR] Scraping failed: {e}")

    # Compare with old file
    old_file = "gozaround/gozaround.txt"
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
