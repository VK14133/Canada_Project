import pytest
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
import shutil
from filter import Filter
from compare_file import CompareFile

def test_scrape_links():
    # Create output folder if it doesn't exist
    output_dir = "idealist"
    os.makedirs(output_dir, exist_ok=True)

    capture_dir = "output"
    os.makedirs(capture_dir, exist_ok=True)

    # Generate timestamped file name
    base_name = os.path.splitext(os.path.basename(__file__))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{base_name}_{timestamp}.txt")

    seen_links = set()   # ✅ keep track of unique links

    scrape_successful = True

    sources = ["AARP","DO_SOMETHING","GOLDEN","IDEALIST","NEWYORKCARES","POINTS_OF_LIGHT","TRANSFORMA","VOLUNTEERGOV"]
    location_types = ["ONSITE","HYBRID","REMOTE"]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            page.goto("https://www.idealist.org/en/volunteer")
            page.wait_for_timeout(3000)

            # Add Filter to filter the opprotuniy based on Source and Location type
            filter = Filter(page)
            filter.clear_location()
            filter.month_filter()

            page.wait_for_timeout(3000)
            
            with open(output_file, "w") as file:
                for source in sources:
                    filter.click_on_source_dorpdown()
                    filter.check_source(source)
                        
                    # Click elsewhere to close dropdown if needed
                    filter.location_input.click()

                    for location_type in location_types:
                        filter.click_on_location_type_dorpdown()
                        filter.check_location_type(location_type)

                        # Click elsewhere to close dropdown if needed
                        filter.location_input.click()
                        filter.page.wait_for_timeout(2000)

                        while True:
                            volunteer_cards = page.locator("//div[@data-qa-id='search-result']//a")

                            card_count = volunteer_cards.count()
                            if card_count == 0:
                                print("[INFO] No volunteer cards found on this page.")
                                break

                            for i in range(card_count):
                                link = volunteer_cards.nth(i).get_attribute("href")
                                if link and link not in seen_links:
                                    seen_links.add(link)
                                    if link.startswith("/"):
                                        file.write(f"https://www.idealist.org{link}\n")
                                    else:
                                        file.write(f"{link}\n")
                                    

                            next_button = page.get_by_role("link", name="Next page")
                            if next_button.count() > 0:
                                class_attr = next_button.get_attribute("class")

                                if class_attr and "gVKght" not in class_attr:
                                    next_button.click()
                                    page.wait_for_timeout(3000)
                                else:
                                    break
                            else:
                                break
                        
        
                        filter.click_on_location_type_dorpdown()
                        filter.uncheck_location_type(location_type)
                        filter.page.locator("body").click()

                    filter.click_on_source_dorpdown()
                    filter.uncheck_source(source)
                    filter.page.locator("body").click()



            browser.close()

    except Exception as e:
        scrape_successful = False
        print(f"[ERROR] Scraping failed: {e}")


    # 🔁 Use CompareFile after scraping is done
    old_file = "idealist/idealist.txt"  # Replace with actual path
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
