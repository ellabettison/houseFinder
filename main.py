from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from house import House
from time import sleep
import pandas as pd

chromedrive_path = '/usr/bin/chromedriver'
chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chromedrive_path, options=chrome_options)

ella_work_locs = ['waterloo+london', 'farringdon+london']
ella_max_travel_time_mins = 35

matt_work_loc = 'imperial+college+london'
matt_max_travel_time_mins = 60

max_crime_rate = 1.5
max_shop_distance = 2
max_any_shop_distance = 0.5
max_train_distance = 3


class HouseFinder:
    def __init__(self, max_price):
        self.max_price = max_price
        self.rightmove_url = f"https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION^87539&maxBedrooms=1&minBedrooms=1&maxPrice={self.max_price}&radius=10.0&sortType=1&propertyTypes=&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=&keywords="

    def find_houses_rightmove(self):
        driver.get(self.rightmove_url)

        houses = []

        for _ in range(20):
            houses_list_container = driver.find_element_by_id("l-searchResults")
            houses_list = houses_list_container.find_elements_by_class_name("l-searchResult")

            for house in houses_list:
                url = house.find_element_by_css_selector('a[data-test="property-details"]')
                address = house.find_element_by_class_name('propertyCard-address')
                price = house.find_element_by_class_name('propertyCard-priceValue')

                new_house = House(url=url.get_attribute("href"), address=address.text,
                                  price=price.text)

                houses.append(new_house)

            next_button = driver.find_element_by_css_selector("button[data-test='pagination-next']")

            if next_button.is_enabled():
                next_button.click()
                sleep(2)
            else:
                break

        return houses
    
    def try_find_cookies(self):
        try:
            cookies_button = driver.find_element_by_css_selector("button[id='save']")
            cookies_button.click()
        except:
            pass

    def find_houses_zoopla(self):
        driver.get(
            f"https://www.zoopla.co.uk/to-rent/property/westminster?beds_max=1&beds_min=1&page_size=25&price_frequency=per_month&price_max={self.max_price}&view_type=list&q=Mayfair%2C+London&radius=10&results_sort=lowest_price&search_source=refine&include_shared_accommodation=false&keywords=-studio")
        houses = []

        sleep(1)

        try:
            cookies_button = driver.find_element_by_css_selector("button[id='save']")
            cookies_button.click()
        except:
            pass

        for i in range(20):
            try:
                houses_list_container = driver.find_element_by_css_selector("main[data-testid='search-content']")
                houses_list = houses_list_container.find_elements_by_css_selector("div[data-testid='search-result']")

                for house in houses_list:
                    url = house.find_element_by_css_selector('a[data-testid="listing-details-link"]')
                    address = house.find_element_by_css_selector("p[data-testid='listing-description']")
                    price = house.find_element_by_css_selector(
                        "div[data-testid='listing-price']").find_element_by_css_selector("p")
    
                    new_house = House(url=url.get_attribute("href"), address=address.text,
                                      price=price.text)
    
                    houses.append(new_house)
            except:
                i -= 1
                self.try_find_cookies()
                continue

            try:
                next_button = driver.find_element_by_xpath("//a[contains(@class, 'PaginationItemNext')]")
            except:
                return houses

            if next_button.get_attribute("aria_disabled") == "false":
                next_button.click()
                sleep(3)
            else:
                return houses

            try:
                alert_button = driver.find_element_by_css_selector("button[data-testid='modal-close']")
                alert_button.click()
            except:
                pass

        return houses

    def find_house_distance(self, house):
        ella_distance = house.get_travel_dist(ella_work_locs[0])
        if ella_distance > ella_max_travel_time_mins:
            ella_distance = house.get_travel_dist(ella_work_locs[1])
        if ella_distance > ella_max_travel_time_mins:
            return ella_distance, 9999999
        matt_distance = house.get_travel_dist(matt_work_loc, ella_dist=False)

        return ella_distance, matt_distance

    def find_suitable_houses(self):
        houses = self.find_houses_rightmove()
        houses += self.find_houses_zoopla()

        suitable_houses = []

        for i, house in enumerate(houses):
            ella_distance, matt_distance = self.find_house_distance(house)
            if ella_distance <= ella_max_travel_time_mins and matt_distance <= matt_max_travel_time_mins:
                suitable_houses.append(house)
                print(f"House {i}/{len(houses)} is SUITABLE    ......    {ella_distance} mins | {matt_distance} mins  "
                      f"| URL: {house.url}")
            else:
                print(f"House {i}/{len(houses)} is UNSUITABLE  ......    {ella_distance} mins | {matt_distance} mins  "
                      f"| URL: {house.url}")

        final_suitable_houses = []

        for house in suitable_houses:
            house.find_area_info()
            if house.crime_rate < max_crime_rate and house.closest_shop_dist < max_shop_distance and house.closest_station_dist < max_train_distance:
                final_suitable_houses.append(house)

        dataframe = pd.DataFrame(
            columns=['Address', 'Price', 'Ella Time', 'Matt Time', 'Crime Rate', 'Closest Shop', 'Shop Distance',
                     'Closest Station', 'Station Distance', 'URL'])

        for house in final_suitable_houses:
            dataframe = dataframe.append({"Address": house.address,
                                          "Price": house.price,
                                          "Ella Time": house.ella_time,
                                          "Matt Time": house.matt_time,
                                          "Crime Rate": house.crime_rate,
                                          "Closest Shop": house.closest_shop,
                                          "Shop Distance": house.closest_shop_dist,
                                          "Closest Station": house.closest_station,
                                          "Station Distance": house.closest_station_dist,
                                          "URL": house.url}, ignore_index=True)

        print(final_suitable_houses)
        with pd.option_context('display.max_rows', None, 'display.max_columns',
                               None):  # more options can be specified also
            print(dataframe)

        dataframe.to_csv("houses.csv")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("doing")
    house_finder = HouseFinder(max_price=1250)
    house_finder.find_suitable_houses()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
