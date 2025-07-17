from playwright.sync_api import Page

class Filter:
    def __init__(self,page:Page):
        self.page = page
        self.location_input = self.page.locator("#page-header-desktop-search-location")
        self.month_dropdown = self.page.locator("#overflow-dropdown")
        self.regency_dropdown = self.page.locator("//details[@data-qa-id='search-facet-accordion-item-recency']")
        self.past_month = self.page.locator("//input[@value='PAST_MONTH']").last
        self.source_dropdown = self.page.locator("//div[@data-qa-id='search-facet-dropdown-source']")
        self.location_type_dropdown = self.page.locator("//div[@data-qa-id='search-facet-dropdown-locationType']")



    # Clear the location
    def clear_location(self):
        self.location_input.wait_for()
        self.location_input.fill("")

    
    # Handle Month Filer
    def month_filter(self):
        self.month_dropdown.wait_for()
        self.month_dropdown.click()
        # self.page.wait_for_timeout(3000)
        self.regency_dropdown.wait_for()
        self.regency_dropdown.click()
        # Check the past month radio box
        # self.page.wait_for_timeout(1000)
        self.past_month.wait_for()
        self.past_month.check()

    def click_on_source_dorpdown(self):
        self.source_dropdown.wait_for()
        self.source_dropdown.click()
        # self.page.wait_for_timeout(3000)

    def check_source(self,source):
        source_checkbox = self.page.locator(f"input[type='checkbox'][value={source}]").first
        source_checkbox.check()
        # self.page.wait_for_timeout(3000)

    def uncheck_source(self,source):
        source_checkbox = self.page.locator(f"input[type='checkbox'][value={source}]").first
        source_checkbox.uncheck()
        # self.page.wait_for_timeout(3000)

    def click_on_location_type_dorpdown(self):
        self.location_type_dropdown.wait_for()
        self.location_type_dropdown.click()
        # self.page.wait_for_timeout(3000)

    def check_location_type(self,location_type):
        source_checkbox = self.page.locator(f"input[type='checkbox'][value={location_type}]").first
        source_checkbox.check()
        # self.page.wait_for_timeout(3000)

    def uncheck_location_type(self,location_type):
        source_checkbox = self.page.locator(f"input[type='checkbox'][value={location_type}]").first
        source_checkbox.uncheck()
        # self.page.wait_for_timeout(3000)