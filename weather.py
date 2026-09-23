import requests
import urllib.request
import json

# Get coordinate
def get_lat_long(zip_code):
    with urllib.request.urlopen(f"http://api.zippopotam.us/us/{zip_code}") as response:
        data = json.loads(response.read().decode())
        place = data['places'][0]
        lat = place['latitude']
        lon = place['longitude']
        return lat, lon

# Helper to parse wind speed numeric value for feels-like calculation
def parse_wind_speed(wind_str):
    try:
        parts = wind_str.split("-")
        return float(parts[0].strip())
    except:
        return 0.0

# Helper to calculate feels-like temperature (Wind Chill or Heat Index)
def calculate_feels_like(temp, wind_speed, humidity):
    if temp <= 50 and wind_speed >= 3:
        # Standard NWS Wind Chill formula
        wc = 35.74 + 0.6215 * temp - 35.75 * (wind_speed ** 0.16) + 0.4275 * temp * (wind_speed ** 0.16)
        return round(wc)
    elif temp >= 80 and humidity is not None:
        # Simplified NOAA Heat Index formula
        hi = (-42.379 + 2.04901523 * temp + 10.14333127 * humidity 
              - 0.22475541 * temp * humidity - 6.83783e-3 * (temp ** 2) 
              - 5.481717e-2 * (humidity ** 2) + 1.22874e-3 * (temp ** 2) * humidity 
              + 8.5282e-4 * temp * (humidity ** 2) - 1.99e-6 * (temp ** 2) * (humidity ** 2))
        return round(hi)
    return temp

# Showing function
def show(point_data, mode, length):
    response = requests.get(point_data.get("properties", {}).get(mode, []))
    data = response.json()
    periods = data.get("properties", {}).get("periods", [])
    
    # Enhanced table format including Feels Like and Humidity
    print(f"{'Time':<11} | {'Tmp':<3} | {'Feel':<4} | {'Hum':<4} | {'Pre':<3} | {'Wind':<9}")
    print("-" * 47)
    
    for period in periods[:length]:
        time = period.get("startTime")[5:13].replace("T"," ").replace("-","/") + "-" + period.get("endTime")[11:13]
        temp = period.get("temperature")
        
        # Get humidity (Note: primarily available in hourly forecasts)
        hum_data = period.get("relativeHumidity", {})
        hum = hum_data.get("value") if hum_data else None
        hum_str = str(hum) if hum is not None else "-"
        
        # Parse wind speed
        wind_raw = period.get("windSpeed", "0 mph")
        wind = wind_raw.replace(" to ","-")[:-4] if " mph" in wind_raw else wind_raw
        wind_val = parse_wind_speed(wind)
        
        # Calculate feels like temperature
        feels = calculate_feels_like(temp, wind_val, hum)
        
        # Precipitation probability
        pre_data = period.get("probabilityOfPrecipitation", {})
        pre = pre_data.get("value")
        pre_str = str(pre) if pre is not None else "0"
        
        print(f"{time:<11} | {temp:<3} | {feels:<4} | {hum_str:<3}% | {pre_str:<2}% | {wind:<9}")

# Main function
def main():
    # Hyperparameters
    latitude = 28.0426686
    longitude = -82.4456614
    days = 7 * 2
    hours = 24

    # Get datapoint
    point_data = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}").json()

    print("Welcome to my weather app")
    while True:
        loc = point_data.get("properties").get("relativeLocation").get("properties")
        print("-------------------------------")
        print(f"Location: {loc.get('city')}, {loc.get('state')}")

        while True:
            print("\n1. Daily")
            print("2. Hourly")
            print("3. Edit location")
            print("4. Change forecast length")
            print("5. Exit")
            choice = int(input("\nYour input: "))
            if choice == 1:
                show(point_data, "forecast", days)
            elif choice == 2:
                show(point_data, "forecastHourly", hours)
            elif choice == 3:
                print("1. Coordinate")
                print("2. Zip code")
                option = int(input("Your choice: "))
                if option == 1:
                    latitude = float(input("Latitude: "))
                    longitude = float(input("Longitude: "))
                elif option == 2:
                    zipcode = input("Zipcode: ")
                    latitude, longitude = get_lat_long(zipcode)
                point_data = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}").json()
                break
            elif choice == 4:
                print("1. Days")
                print("2. Hours")
                option = int(input("Your choice: "))
                if option == 1:
                    days = int(input("Days: ")) * 2
                    hours = 0
                elif option == 2:
                    days = 0
                    hours = int(input("Hours: "))
                break
            elif choice == 5:
                print("Bye (^-^)")
                break
        
        if choice == 5:
            break

if __name__ == "__main__":
    main()