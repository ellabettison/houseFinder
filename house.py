from selenium import webdriver
from time import sleep

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

chromedrive_path = '/usr/bin/chromedriver'
chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chromedrive_path, options=chrome_options)

supermarkets_to_check = ['Tesco', 'Sainsbury', 'Morrisons', 'ASDA', 'ALDI', 'M&S', 'Waitrose', 'Co-op', 'Iceland',
                         'Lidl']


class House:
    def __init__(self, url, address, price):
        self.url = url
        self.address = address
        self.price = price
        self.ella_time = None
        self.matt_time = None
        self.closest_station = None
        self.closest_station_dist = None
        self.closest_shop = None
        self.closest_shop_dist = None
        self.crime_rate = None
        self.closest_gym = None
        self.closest_gym_dist = None

    def __repr__(self):
        return f"address: {self.address}, \t price: {self.price}, \t Ella time: {self.ella_time}, \t Matt time: {self.matt_time}, \t url: {self.url}"

    def get_travel_dist(self, start, ella_dist=True):
        url = f"https://www.google.co.uk/maps/search/{self.address.replace(' ', '+')}+to+{start.replace(' ', '+')}"

        driver.get(url)

        try:
            reject_button = driver.find_element_by_css_selector("button[aria-label='Reject all']")
            reject_button.click()
        except:
            pass

        sleep(2)

        try:
            public_transport_div = driver.find_element_by_css_selector("div[data-travel_mode='3']")
            public_transport_button = public_transport_div.find_element_by_css_selector("button")

            public_transport_button.click()

            sleep(0.5)
        except:
            return 1111111

        try:
            depart_at_div = driver.find_element_by_class_name("goog-menu-button-outer-box")
            depart_at_div.click()

            sleep(0.2)

            menu = driver.find_element_by_class_name("goog-menu-BvBYQ")
            depart_at_option = menu.find_element_by_id(":1")
            depart_at_option.click()

            sleep(0.2)

            time_input = driver.find_element_by_class_name("LgGJQc")
            time_input.send_keys(Keys.CONTROL + "a")
            time_input.send_keys(Keys.DELETE)
            time_input.send_keys("16:00")

            sleep(3)

        except:
            return 2222222

        try:
            distance_section = driver.find_element_by_id('section-directions-trip-0')
            distance = distance_section.find_element_by_xpath("//div[contains(text(),' min')]")
        except:
            return 333333333

        distance = distance.get_attribute('innerHTML')

        mins = distance.split(' min')[0]
        if "hr" in mins:
            mins = mins.split(' hr ')
            mins = int(mins[0]) * 60 + int(mins[1])

        if ella_dist:
            self.ella_time = int(mins)
        else:
            self.matt_time = int(mins)

        return int(mins)

    def check_for_shared_housing(self):
        pass

    def find_area_info(self):
        driver.get(f"https://www.streetcheck.co.uk/search?s={self.address.replace(' ', '+')}")
        sleep(2)
        search_results = driver.find_element_by_css_selector("ul[id='searchresults']")
        first_result = search_results.find_element_by_css_selector('li').find_element_by_css_selector('a')

        postcode = first_result.get_attribute('href').replace('https://www.streetcheck.co.uk/postcode/', '')

        driver.get(f"https://www.postcodearea.co.uk/postaltowns/london/{postcode}/")
        stats = driver.find_elements_by_id("marital-status")

        ethnicities = stats[1]
        unemployment = stats[2]

        ethnicities_info = ethnicities.find_element_by_css_selector("p").text
        unemployment_info = unemployment.find_element_by_css_selector("p").text

        print(ethnicities_info)
        print(unemployment_info)

        # crime rate

        driver.get(f"https://www.postcodearea.co.uk/postaltowns/london/{postcode}/crime/")
        crimes_table = driver.find_element_by_xpath("//table[contains(@class,'table-crime')]")
        crimes_rows = crimes_table.find_elements_by_css_selector("tr")

        crimes_info = []

        total_local_crimes = 0
        total_uk_crimes = 0

        for row in crimes_rows[1:]:
            cols = row.find_elements_by_css_selector("td")
            row_name = cols[0].text
            uk_avg = int(cols[2].text)
            this_area = int(cols[3].text)

            if this_area > uk_avg * 1.5:
                crimes_info.append(
                    f"{row_name} rates are {(int((max(this_area, 1) / max(1, uk_avg)) * 100)) / 100} times the UK average")
            if this_area < uk_avg / 1.5:
                crimes_info.append(
                    f"{row_name} rates are {(int((max(1, uk_avg) / max(1, this_area)) * 100)) / 100} times lower than "
                    f"the UK average")

            total_local_crimes += this_area
            total_uk_crimes += uk_avg

        print(crimes_info)
        self.crime_rate = total_local_crimes / total_uk_crimes
        print(f"crime rate compared to uk average: {self.crime_rate}")

        # closeness to stations

        driver.get(f"https://postcodebyaddress.co.uk/{postcode}")
        train_stations_table = driver.find_element_by_id("railway-stations-table")
        closest_station = train_stations_table.find_elements_by_css_selector("tr")[1]
        closest_station_cols = closest_station.find_elements_by_css_selector("td")
        self.closest_station = closest_station_cols[0].text
        self.closest_station_dist = float(closest_station_cols[1].text[:-2])

        # closest shop

        supermarkets_table = driver.find_element_by_id("supermarkts-table")

        selector = "//td["
        for shop in supermarkets_to_check:
            selector += f"contains(text(),'{shop}')"
            selector += " or "
        selector = selector[:-3]
        selector += "]"

        try:
            closest_supermarket = supermarkets_table.find_elements_by_xpath(selector)[0].find_element_by_xpath('..')
            closest_supermarket_cols = closest_supermarket.find_elements_by_css_selector("td")
            self.closest_shop = closest_supermarket_cols[0].text
            self.closest_shop_dist = float(closest_supermarket_cols[1].text[:-2])
        except:
            self.closest_shop = "None"
            self.closest_shop_dist = 5

        print(self.closest_station, self.closest_station_dist)
        print(self.closest_shop, self.closest_shop_dist)

        print("\n ============= \n")
        
        # closeness to gyms
        
        driver.get(f"https://www.getthedata.com/postcode/{postcode}")
        gyms_table = driver.find_element_by_xpath("//table[contains(text(),'Nearest sports facilities to')]/following-sibling::table")
        print(gyms_table.text)
    

if __name__ == '__main__':
    house = House('www.google.com', 'al35rz', 100)
    house.get_travel_dist('aalborg')
