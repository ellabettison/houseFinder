import argparse

from main import HouseFinder
from termcolor import colored

# max_price, furnished, locs, locs_travel_time, min_bedrooms=1, max_shop_distance=2, max_any_shop_distance=0.5,
# max_train_distance=3, max_crime_rate=3, max_violent_crime_rate=2, search_radius=1

if __name__ == "__main__":
	print(

		colored("""
		 ________  __  __           __                                        
		/        |/  |/  |         /  |                                       
		$$$$$$$$/ $$ |$$ |  ______ $$/_______                                 
		$$ |__    $$ |$$ | /      \$//       |                                
		$$    |   $$ |$$ | $$$$$$  |/$$$$$$$/                                 
		$$$$$/    $$ |$$ | /    $$ |$$      \                                 
		$$ |_____ $$ |$$ |/$$$$$$$ | $$$$$$  |                                
		$$       |$$ |$$ |$$    $$ |/     $$/                                 
		$$$$$$$$/ $$/ $$/  $$$$$$$/ $$$$$$$/                                  
		 ________            __                                               
		/        |          /  |                                              
		$$$$$$$$/   ______  $$/   _______                                     
		$$ |__     /      \ /  | /       |                                    
		$$    |   /$$$$$$  |$$ |/$$$$$$$/                                     
		$$$$$/    $$ |  $$ |$$ |$$ |                                          
		$$ |_____ $$ |__$$ |$$ |$$ \_____                                     
		$$       |$$    $$/ $$ |$$       |                                    
		$$$$$$$$/ $$$$$$$/  $$/  $$$$$$$/                                     
		 __    __ $$ |                                                        
		/  |  /  |$$ |                                                        
		$$ |  $$ |$$/_____   __    __   _______   ______                      
		$$ |__$$ | /      \ /  |  /  | /       | /      \                     
		$$    $$ |/$$$$$$  |$$ |  $$ |/$$$$$$$/ /$$$$$$  |                    
		$$$$$$$$ |$$ |  $$ |$$ |  $$ |$$      \ $$    $$ |                    
		$$ |  $$ |$$ \__$$ |$$ \__$$ | $$$$$$  |$$$$$$$$/                     
		$$ |  $$ |$$    $$/ $$    $$/ /     $$/ $$       |                    
		$$/   $$/  $$$$$$/   $$$$$$/  $$$$$$$/   $$$$$$$/                     
		 ________  __                  __                      __  __  __  __ 
		/        |/  |                /  |                    /  |/  |/  |/  |
		$$$$$$$$/ $$/  _______    ____$$ |  ______    ______  $$ |$$ |$$ |$$ |
		$$ |__    /  |/       \  /    $$ | /      \  /      \ $$ |$$ |$$ |$$ |
		$$    |   $$ |$$$$$$$  |/$$$$$$$ |/$$$$$$  |/$$$$$$  |$$ |$$ |$$ |$$ |
		$$$$$/    $$ |$$ |  $$ |$$ |  $$ |$$    $$ |$$ |  $$/ $$/ $$/ $$/ $$/ 
		$$ |      $$ |$$ |  $$ |$$ \__$$ |$$$$$$$$/ $$ |       __  __  __  __ 
		$$ |      $$ |$$ |  $$ |$$    $$ |$$       |$$ |      /  |/  |/  |/  |
		$$/       $$/ $$/   $$/  $$$$$$$/  $$$$$$$/ $$/       $$/ $$/ $$/ $$/ 
		"""

	,"magenta"))
	
	print(colored("""
	If you haven't already, install geckodriver from here: https://github.com/mozilla/geckodriver/releases
	and change line 14 in main.py to the location you've installed it""", "red"),
	
	colored("""
	and install the requirements with these commands:
		python3 -m venv venv
		source venv/bin/activate
		pip install -r requirements.txt
	"""
, "yellow"),
		
	colored("""
	Run 'python3 run_house_finder.py --help' if youre not sure what to do!!!!
	""", "green"))
	parser = argparse.ArgumentParser(description='FIND SOME HOUSES!!!')
	parser.add_argument('-f', '--furnished', help="House can be unfurnished", action='store_false', default=True)
	parser.add_argument('-p', '--max_price', type=int, help="Max monthly rent price", required=True)
	parser.add_argument('-l', '--locations', type=str, nargs='+',
						help="Locations you want to be close to, anything that can be easily identified by Google Maps, e.g. postcode or street address, in the format: \"loc1\" \"loc2\"",
						required=True)
	parser.add_argument('-t', '--max_travel_times', type=int, nargs='+',
						help="Max travel times for each of the locations you want to be close to in minutes, separated by spaces",
						required=True)
	parser.add_argument('-b', '--min_bedrooms', type=int, help="Minimum number of bedrooms required for house",
						required=True)
	parser.add_argument('-s', '--max_shop_distance', type=int,
						help="Max distance you want from a decent shop in km maybe?", required=False, default=2)
	parser.add_argument('-a', '--max_any_shop', type=int,
						help="Max distance you want from any shop inc shitty corner shop, for emergencies",
						required=False, default=0.5)
	parser.add_argument('-d', '--max_train_dist', type=int,
						help="Max distance you want from a train station in km maybe?", required=False, default=3)
	parser.add_argument('-c', '--max_crime', type=float,
						help="Max crime rate, as compared to UK average, e.g. 1.5 = max 1.5 times the UK average crime rate",
						required=False, default=3)
	parser.add_argument('-v', '--max_violent_crime', type=int,
						help="Max VIOLENT crime rate, as compared to UK average, e.g. 1.5 = max 1.5 times the UK average violent crime rate",
						required=False, default=2)
	parser.add_argument('-r', '--search_radius', type=int,
						help="Radius to search in, in miles, must be one of 1, 3, 5, 10, 15, 20, 30, 40",
						required=False, default=10)

	args = parser.parse_args()
	house_finder = HouseFinder(max_price=args.max_price,
							   furnished=args.furnished,
							   locs=args.locations,
							   locs_travel_time=args.max_travel_times,
							   min_bedrooms=args.min_bedrooms,
							   max_shop_distance=args.max_shop_distance,
							   max_any_shop_distance=args.max_any_shop,
							   max_train_distance=args.max_train_dist,
							   max_crime_rate=args.max_crime,
							   max_violent_crime_rate=args.max_violent_crime,
							   search_radius=args.search_radius
							   )
	suitable_houses = house_finder.find_suitable_houses()
	house_finder.find_houses_info(suitable_houses)
