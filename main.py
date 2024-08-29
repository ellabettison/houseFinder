import csv

import selenium
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from house import House
from time import sleep
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# CHANGE THIS LINE TO YOUR LOCAL GECKODRIVER INSTALL
firefox_path = '/Users/ellabettison/Downloads/geckodriver2'

# chrome_options = FirefoxOptions()
# # chrome_options.add_argument('--lang=en_US')
# # chrome_options.add_argument('--disable-gpu')
# # chrome_options.add_argument('--window-size=1024,768')
# chrome_options.add_argument("--headless")
# # chrome_options.add_argument('--disable-browser-side-navigation')
# caps = DesiredCapabilities().FIREFOX
# # caps["pageLoadStrategy"] = "eager"
# # chrome_options.page_load_strategy = 'eager'
# driver = webdriver.Firefox(executable_path=firefox_path, desired_capabilities=caps, options=chrome_options)

options = webdriver.FirefoxOptions()
# options.binary = firefox_path
# options.add_argument('start-maximized')
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)


# ella_work_locs = ['120 Moorgate, London EC2M 6UR']
# ella_max_travel_time_mins = 50
# 
# matt_work_loc = 'imperial+college+london'
# matt_max_travel_time_mins = 50
# 
# max_crime_rate = 3
# 
# max_theft_rate = 3
# max_violent_crime_rate = 2
# 
# max_shop_distance = 2
# max_any_shop_distance = 0.5
# max_train_distance = 3
# 
# search_radius = 20.0  # 10.0
# max_price = 1350
# 
# furnished = False


# furnished%2CpartFurnished

class HouseFinder:
	def __init__(self, max_price, furnished, locs, locs_travel_time, min_bedrooms=4, max_shop_distance=2,
				 max_any_shop_distance=0.5,
				 max_train_distance=3, max_crime_rate=3, max_violent_crime_rate=2, search_radius=3, crimes_types=[],
				 max_bedrooms=4,
				 buying=False):
		self.max_price = max_price
		self.furnished = furnished
		self.locs = locs
		self.locs_travel_time = locs_travel_time
		self.max_shop_distance = max_shop_distance
		self.max_any_shop_distance = max_any_shop_distance
		self.max_train_distance = max_train_distance
		self.max_crime_rate = max_crime_rate
		self.max_violent_crime_rate = max_violent_crime_rate
		self.search_radius = search_radius  # 1/4, 1/2, 1, 3, 5, 10, 15, 20, 30, 40 miles
		self.min_bedrooms = min_bedrooms
		self.crimes_types = crimes_types
		self.max_bedrooms = max_bedrooms
		self.buying = buying

		furnished_str = "furnishTypes="
		if furnished:
			furnished_str = "furnishTypes=furnished%2CpartFurnished"  # REGION^87490= london#POSTCODE^15515 birmingham
		if buying:
			buying_str = 'for-sale'
		else:
			buying_str = 'to-rent'
		self.rightmove_url = f"https://www.rightmove.co.uk/property-{buying_str}/find.html?locationIdentifier=REGION^87490&propertyTypes=bungalow%2Cdetached%2Csemi-detached%2Cterraced&minBedrooms={self.min_bedrooms}&maxBedrooms={self.max_bedrooms}&minPrice=200000&maxPrice={self.max_price}&radius={search_radius}&sortType=1&propertyTypes=&mustHave=&dontShow=houseShare%2Cretirement&{furnished_str}&keywords="

	def find_houses_rightmove(self):
		driver.get(self.rightmove_url)

		houses = []
		curr_url = self.rightmove_url
		for page in range(20):
			houses_in_curr_page = 0
			try:
				houses_list_container = WebDriverWait(driver, 5, poll_frequency=0.1).until(
					EC.visibility_of_element_located((By.ID, "l-searchResults")))
				curr_url = driver.current_url
				# houses_list_container = driver.find_element_by_id("l-searchResults")
				houses_list = houses_list_container.find_elements(By.CLASS_NAME, "l-searchResult")

				for i in range(1, len(houses_list)):
					houses_list_container = WebDriverWait(driver, 5, poll_frequency=0.1).until(
						EC.visibility_of_element_located((By.ID, "l-searchResults")))
					# houses_list_container = driver.find_element_by_id("l-searchResults")
					houses_list = houses_list_container.find_elements(By.CLASS_NAME, "l-searchResult")
					house = houses_list[i]
					url = house.find_element(By.CSS_SELECTOR, 'a[data-test="property-details"]').get_attribute("href")
					address = house.find_element(By.CLASS_NAME, 'propertyCard-address').text
					price = house.find_element(By.CLASS_NAME, 'propertyCard-priceValue').text

					driver.get(url)
					leasehold = driver.find_element(By.CSS_SELECTOR, 'dl[data-test="infoReel"]')

					if "leasehold" in leasehold.text.lower():
						driver.get(curr_url)
						houses_list_container = WebDriverWait(driver, 5, poll_frequency=0.1).until(
							EC.visibility_of_element_located((By.ID, "l-searchResults")))
						# houses_list_container = driver.find_element_by_id("l-searchResults")
						houses_list = houses_list_container.find_elements(By.CLASS_NAME, "l-searchResult")
						continue

					new_house = House(url=url, address=address,
									  price=price, locs=self.locs, radius=self.search_radius,
									  crime_types=self.crimes_types)

					houses.append(new_house)
					houses_in_curr_page += 1

					driver.get(curr_url)
					sleep(1)

				next_button = driver.find_element(by=By.CSS_SELECTOR, value="button[data-test='pagination-next']")

				if next_button.is_enabled():
					print(f'Found {houses_in_curr_page} houses in page {page}/20')
					next_button.click()
					sleep(2)
				else:
					break
			except exceptions.ElementClickInterceptedException as e:
				print(e)
				# try:
				sleep(1)
				cookies_button = driver.find_element(by=By.ID, value="onetrust-reject-all-handler")
				cookies_button.click()
				sleep(1)
				driver.get(curr_url)
			#     except Exception as e:
			#         print(e)
			#         pass
			#     pass

		return houses

	def try_find_cookies(self, mydriver):
		print("trying to find cookies")
		# try:
		# for i in range(4):
		sleep(1)
		#     try:
		#         driver.switch_to.default_content()
		#         # iframe = driver.find_element(By.XPATH, "//iframe[id='gdpr-consent-notice']")
		#         # driver.switch_to.frame(iframe)
		#         driver.switch_to.frame(i)
		#     except Exception as e:
		#         print(e)
		#     cookies = driver.find_element(By.XPATH, "//button[contains(id, 'save')]")
		#     sleep(1)
		#     cookies.click()
		#     driver.switch_to.default_content()

		# driver.switch_to.default_content()
		iframe = mydriver.find_elements(By.XPATH, "//iframe")
		for fr in iframe:

			try:
				print(f"frame: {fr.accessible_name}")
				# driver.switch_to.frame(fr)
				WebDriverWait(mydriver, 5, poll_frequency=0.1).until(EC.frame_to_be_available_and_switch_to_it(fr))
				cookies = mydriver.find_elements(By.CSS_SELECTOR, "button[id='save']")[0]
				WebDriverWait(mydriver, 5, poll_frequency=0.1).until(EC.element_to_be_clickable(cookies))
				# cookies = driver.find_elements(By.XPATH, "//button[contains(id, 'save')]")
				cookies.click()
				mydriver.switch_to.default_content()
			except Exception as e:
				mydriver.switch_to.default_content()
				# print(e)

			# print([fr for fr in iframe])
			# # 
			# print("found iframe")
			# driver.switch_to.frame(iframe)
			# print("switched to iframe")
			# cookies_button = driver.find_element_by_xpath("//button[contains(@id, 'save')]")
			# cookies_button.click()
			# driver.switch_to.default_content()
		# except Exception as e:
		#     print(e)
		#     print("could not find")
		#     pass

	# furnished_state=furnished

	def find_houses_zoopla(self):
		mydriver = webdriver.Firefox(executable_path=firefox_path, desired_capabilities=caps, options=chrome_options)
		furnished_str = ""
		if self.furnished:
			furnished_str = "&furnished_state=furnished"
		url_str = f"https://www.zoopla.co.uk/to-rent/property/westminster?beds_max=1&beds_min=1&page_size=25&price_frequency=per_month&price_max={self.max_price}&view_type=list&q=Mayfair%2C+London&radius={int(self.search_radius)}&results_sort=lowest_price&search_source=refine&include_shared_accommodation=false&keywords=-studio{furnished_str}"
		mydriver.get(url_str
					 )
		houses = []

		self.try_find_cookies(mydriver)

		for i in range(5):
			try:

				# sleep(2)
				# self.try_find_cookies()
				sleep(2)
				houses_list_container = WebDriverWait(mydriver, 5, poll_frequency=0.1).until(
					EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='regular-listings']")))
				houses_list = houses_list_container.find_elements(By.CSS_SELECTOR, "div[id^='listing']")
				# houses_list_container = driver.find_element_by_css_selector("section[data-testid='search-content']")
				# houses_list = houses_list_container.find_elements_by_css_selector("div[data-testid='search-result']")

				for house in houses_list:
					url = house.find_element_by_css_selector('a[href^="/to-rent/details"]')
					# url = house.find_element_by_css_selector('a[data-testid="listing-details-link"]')
					address = WebDriverWait(house, 5, poll_frequency=0.1).until(
						EC.visibility_of_element_located(
							(By.CSS_SELECTOR, "address")))

					# address = house.find_element_by_xpath("//h2[data-testid='listing-title']/following-sibling::address")
					price = house.find_element_by_css_selector(
						"p[data-testid='listing-price']")

					new_house = House(url=url.get_attribute("href"), address=address.text,
									  price=price.text, locs=self.locs, radius=self.search_radius,
									  crime_types=self.crimes_types)
					# print("FOUND ZOOPLA HOUSE: ", new_house)
					houses.append(new_house)
					# except Exception as e:
					#     print(e)
					#     i += 1
					#     # cookies = driver.find_element(By.XPATH, "//span[contains(text(), 'Accept all cookies')]")
					#     # cookies.click()
					#     self.try_find_cookies()
					#     continue

					# try:
					sleep(1.1)
					mydriver = webdriver.Firefox(executable_path=firefox_path, desired_capabilities=caps,
												 options=chrome_options)
					sleep(3)
					mydriver.get(url_str + f"&pn={i + 1}")
					sleep(3)

					mydriver.get(url_str + f"&pn={i + 1}")

					sleep(3)
			# next_button = WebDriverWait(driver, 5, poll_frequency=0.1).until(
			#     EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Next >')]")))
			# # next_button = driver.find_element_by_xpath("//a[contains(text(), 'Next >')]")
			# if next_button.get_attribute("aria-disabled") == "false":
			#     next_button.click()
			# else:
			#     print("next button disabled")
			#     return houses
			except Exception as e:
				# print(e)
				print("cant find next button")
				i += 1
				#     # try:
				#     # cookies = driver.find_element(By.XPATH, "//span[contains(text(), 'Accept all cookies')]")
				#     # cookies.click()
				#   

				sleep(2)
				self.try_find_cookies(mydriver)
				sleep(2)
			#     continue

			# try:
			#     alert_button = WebDriverWait(driver, 5, poll_frequency=0.1).until(
			#         EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='modal-close']")))
			#     # alert_button = driver.find_element_by_css_selector("button[data-testid='modal-close']")
			#     alert_button.click()
			# except Exception as e:
			#     print(e)
			#     pass

		return houses

	def find_house_distance(self, house):
		dists = []
		for i in range(min(len(self.locs), len(self.locs_travel_time))):
			curr_dist = house.get_travel_dist(self.locs[i])
			dists.append(curr_dist)
			if curr_dist > self.locs_travel_time[i]:
				return dists
		# matt_distance = house.get_travel_dist(matt_work_loc, ella_dist=False)

		# if matt_distance > matt_max_travel_time_mins:
		#     return 9999999, matt_distance
		# ella_distance = house.get_travel_dist(ella_work_locs[0])
		# if ella_distance > ella_max_travel_time_mins:
		#     ella_distance = house.get_travel_dist(ella_work_locs[1])

		return dists

	def find_suitable_houses(self):

		houses = self.find_houses_rightmove()
		# houses += self.find_houses_zoopla()

		suitable_houses = []

		df_suitable_houses = pd.DataFrame(
			columns=['Address', 'Price', 'Ella Time', 'Matt Time', 'URL'])

		for i, house in enumerate(houses):
			try:
				price = house.price.replace("pcm", "")
				price = price.replace("£", "")
				price = price.replace(",", "")
				if int(price) > self.max_price:
					continue
				else:
					house.price = price
			except:
				pass
			dists = self.find_house_distance(house)
			any_dist_bad = any([dists[i] > self.locs_travel_time[i] for i in range(len(dists))])
			house_dist_list = [f"\t{self.locs[i].upper()} DIST: {dists[i] if i < len(dists) else 'Skipped'} mins\t|" for
							   i in range(len(self.locs))]
			house_dist_str = ''.join(house_dist_list)
			if not any_dist_bad:
				suitable_houses.append(house)

				print(
					f"House {i}/{len(houses)} is SUITABLE\t......\t£{house.price} pcm\t|" + house_dist_str +
					f"\tURL: {house.url}")
				dists_dict = {f"{self.locs[i]} dist:": house_dist_list[i] for i in range(len(self.locs))}
				new_dict_line = {"Address": house.address,
								 "Price": house.price,
								 "URL": house.url} | dists_dict
				# df_suitable_houses = df_suitable_houses.append(new_dict_line, ignore_index=True)
				new_dict_line = pd.Series(new_dict_line)
				df_suitable_houses = pd.concat([df_suitable_houses, new_dict_line], ignore_index=True)
				# print(df_suitable_houses)
				with open("curr_houses.csv", 'wb') as f:
					df_suitable_houses.to_csv(f)

			else:
				print(
					f"House {i}/{len(houses)} is UNSUITABLE\t......\t£{house.price} pcm\t|" + house_dist_str +
					f"| URL: {house.url}")
		return suitable_houses

	def load_houses_from_csv(self, csv_file):
		houses = []
		with open(csv_file, 'r') as f:
			reader = csv.DictReader(f)
			for row in reader:
				new_house = House(url=row['URL'], address=row['Address'],
								  price=row['Price'])
				new_house.ella_time = row['Ella Time']
				new_house.matt_time = row['Matt Time']
				houses.append(new_house)
		return houses

	def find_houses_info(self, suitable_houses):

		final_suitable_houses = []

		for house in suitable_houses:
			print(f"\n ===== \n")
			print(f"{house.address}")
			print(house.url)
			house.find_area_info()
			# if house.theft_rate < max_theft_rate and house.violent_crime_rate < max_violent_crime_rate and house.closest_shop_dist < max_shop_distance and house.closest_station_dist < max_train_distance:
			price = str(house.price).replace("pcm", "")
			price = price.replace("£", "")
			price = price.replace(",", "")
			house.price = int(price)

			if house.price < self.max_price:
				final_suitable_houses.append(house)

		dataframe = pd.DataFrame(
			columns=['Address', 'Price', 'Crime Rate', 'Closest Shop', 'Shop Distance',
					 'Closest Station', 'Station Distance', 'Closest Gym', 'URL'] + [f"{loc} Time" for loc in
																					 self.locs] + [f"{crime} Rate" for
																								   crime in
																								   self.crimes_types])

		for house in final_suitable_houses:
			dists_dict = {f"{self.locs[i]} Time": house.travel_times[i] for i in range(len(self.locs))}
			self.crimes_types = ["Theft", "Violent Crimes", "Burglary"]
			house.crimes = [house.theft_rate, house.violent_crime_rate, house.burglary_rate]
			crimes_dict = {f"{self.crimes_types[i]} Rate": house.crimes[i] for i in range(len(self.crimes_types))}
			dataframe = dataframe.append({"Address": house.address,
										  "Price": house.price,
										  "Crime Rate": house.crime_rate,
										  "Closest Shop": house.closest_shop,
										  "Shop Distance": house.closest_shop_dist,
										  "Closest Station": house.closest_station,
										  "Station Distance": house.closest_station_dist,
										  "Closest Gym": (
											  house.closest_gym if house.closest_gym is not None else '').replace('\n',
																												  ''),
										  "URL": house.url} | dists_dict | crimes_dict, ignore_index=True)

		print(final_suitable_houses)
		with pd.option_context('display.max_rows', None, 'display.max_columns',
							   None, 'display.width', 1000):  # more options can be specified also
			print(dataframe)

		dataframe.to_csv("houses.csv")


if __name__ == '__main__':
	print("doing")
	house_finder = HouseFinder(max_price=1350, furnished=False, locs=['120 moorgate'], locs_travel_time=[60])
	suitable_houses = house_finder.find_suitable_houses()
	# suitable_houses = house_finder.load_houses_from_csv("curr_houses.csv")
	house_finder.find_houses_info(suitable_houses)
