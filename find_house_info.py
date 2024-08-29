import sys
import pandas as pd
from house import House
from main import HouseFinder

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    house = House(url=sys.argv[1], address=sys.argv[2],
                  price=sys.argv[3])

    house_finder = HouseFinder(max_price=1500)

    ella_distance, matt_distance = house_finder.find_house_distance(house)
    house.find_area_info()

    dataframe = pd.DataFrame(
        columns=['Address', 'Price', 'Ella Time', 'Matt Time', 'Crime Rate', 'Closest Shop', 'Shop Distance',
                 'Closest Station', 'Station Distance', 'Closest Gym', 'URL'])

    dataframe = dataframe.append({"Address": house.address,
                                  "Price": house.price,
                                  "Ella Time": house.ella_time,
                                  "Matt Time": house.matt_time,
                                  "Crime Rate": house.crime_rate,
                                  "Theft Rate": house.theft_rate,
                                  "Violent Crime Rate": house.violent_crime_rate,
                                  "Closest Shop": house.closest_shop,
                                  "Shop Distance": house.closest_shop_dist,
                                  "Closest Station": house.closest_station,
                                  "Station Distance": house.closest_station_dist,
                                  "Closest Gym": house.closest_gym,
                                  "URL": house.url}, ignore_index=True)

    with pd.option_context('display.max_rows', None, 'display.max_columns',
                           None, 'display.width', 1000):  # more options can be specified also
        print(dataframe)

    dataframe.to_csv("new_house.csv")
