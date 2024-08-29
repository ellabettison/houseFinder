from selenium import webdriver
from time import sleep

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# chromedrive_path = '/usr/local/bin/chromedriver'
firefox_path = '/Users/ellabettison/Downloads/geckodriver'
# chrome_options = FirefoxOptions()
# chrome_options.add_argument('--lang=en_US')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--window-size=1024,768')
# chrome_options.add_argument("--headless")
# chrome_options.add_argument('--disable-browser-side-navigation')
# caps = DesiredCapabilities().FIREFOX
# caps["pageLoadStrategy"] = "eager"
# chrome_options.page_load_strategy = 'eager'
# binary = '/usr/bin/firefox'
options = webdriver.FirefoxOptions()
# options.binary = firefox_path
# options.add_argument('start-maximized')
options.add_argument('--headless')
driver = webdriver.Firefox(options=options) #, desired_capabilities=caps, options=chrome_options)
driver.command_executor.set_timeout(10)

supermarkets_to_check = ['Tesco', 'Sainsbury', 'Morrisons', 'ASDA', 'ALDI', 'M&S', 'Waitrose', 'Co-op', 'Iceland',
                         'Lidl']

crime = ['Violent Crimes', 'Burglary', 'Theft']
crime_radius = 3
crime_radius_deg = crime_radius / 69
#[{'url': 'all-crime', 'name': 'All crime'}, {'url': 'anti-social-behaviour', 'name': 'Anti-social behaviour'}, 
# {'url': 'bicycle-theft', 'name': 'Bicycle theft'}, {'url': 'burglary', 'name': 'Burglary'}, 
# {'url': 'criminal-damage-arson', 'name': 'Criminal damage and arson'}, {'url': 'drugs', 'name': 'Drugs'}, 
# {'url': 'other-theft', 'name': 'Other theft'}, {'url': 'possession-of-weapons', 'name': 'Possession of weapons'}, 
# {'url': 'public-order', 'name': 'Public order'}, {'url': 'robbery', 'name': 'Robbery'}, 
# {'url': 'shoplifting', 'name': 'Shoplifting'}, {'url': 'theft-from-the-person', 'name': 'Theft from the person'}, 
# {'url': 'vehicle-crime', 'name': 'Vehicle crime'}, {'url': 'violent-crime', 'name': 'Violence and sexual offences'}, 
# {'url': 'other-crime', 'name': 'Other crime'}]

crime_cats = ['violent-crime', 'burglary', 'theft-from-the-person']


class House:
    def __init__(self, url, address, price, locs, radius, crime_types):
        self.url = url
        self.address = address
        self.price = price
        # self.ella_time = None
        # self.matt_time = None
        self.locs = locs
        self.closest_station = None
        self.closest_station_dist = 9999
        self.closest_shop = None
        self.closest_shop_dist = 9999
        self.crime_rate = 9999
        self.theft_rate = 9999
        self.burglary_rate = 9999
        self.violent_crime_rate = 9999
        self.crimes = []
        self.crimes_types = crime_types
        self.closest_gym = None
        self.closest_gym_dist = 9999
        self.travel_times = []
        self.search_radius = radius

    def __repr__(self):
        dists_dict = [f"{self.locs[i]} dist: {self.travel_times[i]}" for i in range(len(self.locs))]
        return f"address: {self.address}, \t price: {self.price}, \t url: {self.url}" + '\t'.join(dists_dict)

    def wait_until(self, a_driver, condition, timeout=10):

        timer = timeout
        while (not condition()) and timer > 0:
            sleep(0.5)
            timer -= 0.5

        sleep(500)

    def get_travel_dist(self, start, ella_dist=True):
        url = f"https://www.google.co.uk/maps/search/{self.address.replace(' ', '+')}+to+{start.replace(' ', '+')}"

        try:
            driver.get(url)
            
        except:
            self.travel_times.append(-1)
            return -1

        try:
            # reject_button = driver.find_element_by_css_selector("button[aria-label='Reject all']")
            reject_button = WebDriverWait(driver, 1, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button["
                                                                   "aria-label='Reject all']")))
            reject_button.click()
        except:
            pass

        try:
            # public_transport_div = driver.find_element_by_css_selector("div[data-travel_mode='3']")
            public_transport_div = WebDriverWait(driver, 15, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-travel_mode='3']")))
            # public_transport_button = public_transport_div.find_element_by_css_selector("button")
            
            public_transport_button = WebDriverWait(driver, 5, poll_frequency=0.1).until(
                EC.visibility_of(public_transport_div.find_element(By.CSS_SELECTOR, "button")))
    
            # public_transport_mins = WebDriverWait(driver, 5, poll_frequency=0.1).until(
            #     EC.visibility_of(public_transport_button.find_element(By.XPATH, "//div[contains(text(),' min')]")))
            # 
            # distance = public_transport_button.get_attribute('innerHTML')
            distance = public_transport_button.text
            # 
            mins = distance.split(' min')[0]
            if "hr" in mins:
                mins = mins.split(' hr ')
                mins = int(mins[0]) * 60 + int(mins[1])
    
            # if ella_dist:
            #     self.ella_time = int(mins)
            # else:
            #     self.matt_time = int(mins)
            self.travel_times.append(int(mins))
    
            return int(mins)
        
                # public_transport_button.click()

        except Exception as e:
            print(e)
            self.travel_times.append(-1)
            return -1

        # try:
        # # depart_at_div = driver.find_element_by_class_name("goog-menu-button-outer-box")
        #     depart_at_div = WebDriverWait(driver, 10, poll_frequency=0.1).until(
        #         EC.visibility_of_element_located((By.CLASS_NAME, "goog-menu"
        #                                                          "-button-outer-box")))
        #     depart_at_div.click()
        # 
        #     # menu = driver.find_element_by_class_name("goog-menu-BvBYQ")
        #     menu = WebDriverWait(driver, 10, poll_frequency=0.1).until(
        #         EC.visibility_of_element_located((By.CLASS_NAME, "goog-menu-BvBYQ")))
        #     depart_at_option = WebDriverWait(driver, 10, poll_frequency=0.1).until(
        #         EC.visibility_of(menu.find_element(By.ID, ":1")))
        #     # depart_at_option = menu.find_element_by_id(":1")
        #     depart_at_option.click()
        # 
        #     # time_input = driver.find_element_by_class_name("LgGJQc")
        #     time_input = WebDriverWait(driver, 10, poll_frequency=0.1).until(
        #         EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='transit-time']")))
        #     time_input.send_keys(Keys.COMMAND + "a")
        #     time_input.send_keys(Keys.DELETE)
        #     time_input.send_keys("16:00")
        # 
        # except:
        #     return 2222222

        # sleep(2) 

        # try:
            #<span class="Os0QJc google-symbols G47vBd" aria-label="Walking" role="img"></span>
            # WebDriverWait(driver, 10, poll_frequency=0.5).until(
            #     EC.visibility_of_element_located((By.XPATH, '//span[@id="section-directions-trip-travel-mode-0"]//span[@aria-label="Walking"]'))
            # )
            # # distance_section = driver.find_element_by_id('section-directions-trip-0')
            # distance_section = WebDriverWait(driver, 10, poll_frequency=0.1).until(
            #     EC.visibility_of_element_located((By.ID, 'section-directions-trip-0')))
            # distance = WebDriverWait(driver, 10, poll_frequency=0.1).until(
            #     EC.visibility_of(distance_section.find_element(By.XPATH, "//div[contains(text(),' min')]")))
            # # distance = distance_section.find_element_by_xpath("//div[contains(text(),' min')]")
            # distance = distance.get_attribute('innerHTML')
            # 
            # mins = distance.split(' min')[0]
            # if "hr" in mins:
            #     mins = mins.split(' hr ')
            #     mins = int(mins[0]) * 60 + int(mins[1])
            # 
            # # if ella_dist:
            # #     self.ella_time = int(mins)
            # # else:
            # #     self.matt_time = int(mins)
            # self.travel_times.append(int(mins))
            # 
            # return int(mins)

        # except:
        #     return 333333333

    def check_for_shared_housing(self):
        pass

    def find_area_info(self):
        try:
            print("getting street check")
            driver.get(f"https://www.streetcheck.co.uk/search?s={self.address.replace(' ', '+')}")
            print("got street check")
            search_results = WebDriverWait(driver, 10, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "ul[id='searchresults']")))
            # search_results = driver.find_element_by_css_selector("ul[id='searchresults']")
            
            first_result = search_results.find_element(By.CSS_SELECTOR, "li").find_element(By.CSS_SELECTOR, 'a')
            # first_result = search_results.find_element_by_css_selector('li').find_element_by_css_selector('a')
    
            postcode = first_result.get_attribute('href').replace('https://www.streetcheck.co.uk/postcode/', '')
            print(f"got postcode: {postcode}")
        except:
            print("AAH ERROR")
            return 
            

        # crime rate

        try:
            # print("getting postcode check")
            # driver.get(f"https://www.postcodearea.co.uk/postaltowns/london/{postcode}/crime/")
            driver.execute_script(
                f"window.location.href = 'https://www.postcodearea.co.uk/postaltowns/london/{postcode}/crime/';")
            # print("got street check")
            crimes_table = WebDriverWait(driver, 5, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.XPATH, "//table[contains(@class,'table-crime')]")))
            # crimes_table = driver.find_element_by_xpath("//table[contains(@class,'table-crime')]")
            crimes_rows = crimes_table.find_elements(By.CSS_SELECTOR, "tr")

            crimes_info = []

            total_local_crimes = 0
            total_uk_crimes = 0

            for row in crimes_rows[1:]:
                cols = row.find_elements(By.CSS_SELECTOR, "td")
                row_name = cols[0].text
                uk_avg = int(cols[2].text)
                this_area = int(cols[3].text)

                if row_name == "Theft":
                    self.theft_rate = (int((max(this_area, 1) / max(1, uk_avg)) * 100)) / 100
                elif row_name == "Violent Crimes":
                    self.violent_crime_rate = (int((max(this_area, 1) / max(1, uk_avg)) * 100)) / 100
                elif row_name == "Burglary":
                    self.burglary_rate = (int((max(this_area, 1) / max(1, uk_avg)) * 100)) / 100

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
            # print(f"crime rate: {self.crime_rate} times UK average")

            # print("got crimes")
        except:
            self.crime_rate = 99999

        # closeness to stations

        try:
            # print("getting postcodes by address")
            driver.execute_script(f"window.location.href = 'https://postcodebyaddress.co.uk/{postcode}';")
            # driver.get(f"https://postcodebyaddress.co.uk/{postcode}")
            # print("got postcode by address")
            train_stations_table = WebDriverWait(driver, 5, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.ID, "railway-stations-table")))
            # train_stations_table = driver.find_element_by_id("railway-stations-table")
            closest_station = train_stations_table.find_elements(By.CSS_SELECTOR, "tr")[1]
            closest_station_cols = closest_station.find_elements(By.CSS_SELECTOR, "td")
            self.closest_station = closest_station_cols[0].text
            self.closest_station_dist = float(closest_station_cols[1].text[:-2])
            # print("got railway stations")

            # closest shop

            supermarkets_table = driver.find_element(By.ID, "supermarkts-table")

            selector = "//td["
            for shop in supermarkets_to_check:
                selector += f"contains(text(),'{shop}')"
                selector += " or "
            selector = selector[:-3]
            selector += "]"

            try:
                closest_supermarket = supermarkets_table.find_elements(By.XPATH, selector)[0].find_element(By.XPATH, '..')
                closest_supermarket_cols = closest_supermarket.find_elements(By.CSS_SELECTOR, "td")
                self.closest_shop = closest_supermarket_cols[0].text
                self.closest_shop_dist = float(closest_supermarket_cols[1].text[:-2])
            except:
                self.closest_shop = "None"
                self.closest_shop_dist = 5

            # print("got shops")

            print("Closest station: ", self.closest_station, self.closest_station_dist)
            print("Closest shop: ", self.closest_shop, self.closest_shop_dist)

        except:
            self.closest_shop = "None"
            self.closest_shop_dist = 9999
            self.closest_station = "None"
            self.closest_station_dist = 9999

        # try:

        AVG_LONDON = 700*3

        # par_lat = WebDriverWait(driver, 2, poll_frequency=0.1).until(
        #     EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Latitude')]/parent::tr")))
        # # par_lat = child_lat.find_element((By.XPATH, '..'))
        # lat = float(par_lat.find_elements(By.TAG_NAME, 'td')[1].text)
        # 
        # par_long = WebDriverWait(driver, 2, poll_frequency=0.1).until(
        #     EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Longitude')]/parent::tr")))
        # par_long = child_long.find_element((By.XPATH, '..'))
        # long = float(par_long.find_elements(By.TAG_NAME, 'td')[1].text)

        import requests

        # url = f'https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={long}'
        # poly = ""
        # for coords in [[-1, -1], [-1, 1], [1, 1], [1, -1]]:
        #     i, j = coords
        #     poly += f"{str(lat + i * self.search_radius/2)},{str(long + j * self.search_radius/2)}"
        #     poly += ":"
        # 
        # try:
        #     url = f'https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={long}'
        #     x = requests.get(url)
        #     data = x.json()
        # 
        #     crime_number = len(data)
        # 
        #     url = f'https://data.police.uk/api/crimes-street/all-crime?poly={poly}' #poly={poly[:-1]}'
        #     x = requests.get(url)
        #     data = x.json()
        #     total_crime_rate = len(data)/((self.search_radius)**2)
        #     
        #     crime_ratio = crime_number / total_crime_rate
        #     print(f"crime number in last year in 1 mile radius: {crime_number}, crime ratio compared to UK average: {crime_ratio}")
        # 
        #     self.crime_rate = crime_ratio
        # except Exception:
        #     pass
        # 
        # for type in self.crimes_types:
        #     print(type, lat, long)
        #     
        #     # try:
        #     url = f'https://data.police.uk/api/crimes-street/{type}?lat={lat}&lng={long}' #poly={poly[:-1]}'
        #     print(url)
        #     x = requests.get(url)
        #     print(x)
        #     data = x.json()
        #     crime_rate = len(data)
        # 
        #     url = f'https://data.police.uk/api/crimes-street/{type}?poly={poly}' #poly={poly[:-1]}'
        #     print(url)
        #     x = requests.get(url)
        #     print(x)
        #     data = x.json()
        #     total_crime_rate = len(data)/((self.search_radius)**2)
        #     
        #     self.crimes.append(crime_rate/total_crime_rate)
        # 
        #     print(f"{type} number in last year in 1 mile radius: {self.crimes[-1]}")
            # except Exception as e:
            #     self.crimes.append(-1)
            #     print(e)

        # try:
        #     url = f'https://data.police.uk/api/crimes-street/burglary?poly={poly[:-1]}'
        #     x = requests.post(url)
        #     data = x.json()
        #     self.burglary_rate = len(data)
        # 
        #     print(f"burglary number in last year in 1 mile radius: {self.burglary_rate}")
        # except Exception:
        #     pass
        # 
        # 
        # try:
        #     url = f'https://data.police.uk/api/crimes-street/theft-from-the-person?poly={poly[:-1]}'
        #     x = requests.post(url)
        #     data = x.json()
        #     self.theft_rate = len(data)
        # 
        #     print(f"theft number in last year in 1 mile radius: {self.theft_rate}")
        # except Exception:
        #     pass

        # except Exception as e:
        # #     print(e)
        #     pass

        # closeness to gyms

        try:
            # print("getting gyms page")
            upper_postcode = postcode.upper()
            driver.get(f"https://www.getthedata.com/postcode/{upper_postcode[:-3]}-{upper_postcode[-3:]}")
            # print("got gyms page")

            try:
                gyms_table = driver.find_element(By.XPATH, "//td[contains(text(),'Health and Fitness Gym')]")
                print("Closest gym: ",gyms_table.text)
                self.closest_gym = gyms_table.text
            except:
                consent_btn = driver.find_element(By.XPATH, "//p[contains(text(),'Consent')]")
                consent_btn.click()
                try:
                    gyms_table = driver.find_element(By.XPATH, "//td[contains(text(),'Heath and Fitness Gym')]")
                    print("Closest gym: ", gyms_table.text)
                    self.closest_gym = gyms_table.text
                except:
                    pass
            # print("got gyms")
        except:
            self.closest_gym = "None"


if __name__ == '__main__':
    house = House('www.google.com', 'al35rz', 100)
    house.get_travel_dist('aalborg')
