import requests

# Showing function
def show(point_data, mode, length):
    response = requests.get(point_data.get("properties", {}).get(mode, []))
    data = response.json()
    periods = data.get("properties", {}).get("periods", [])
    print(f"{'Time':<16} | {'Tem':<4} | {'Pre':<3} | {'Wind':<9}")
    print("-" * 39)
    for period in periods[:length]:
        time = period.get("startTime")[:13].replace("T"," ") + "-" + period.get("endTime")[11:13]
        temp = str(period.get("temperature"))
        pre = period.get("probabilityOfPrecipitation", {}).get("value")
        wind = period.get("windSpeed").replace(" to ","-")
        print(f"{time:<16} | {temp:<3}F | {pre:<2}% | {wind:<9}")


# Main function
def main():
    # Hyperparameters
    latitude = 35.1443
    longitude = -111.6664
    days = 7*2
    hours = 24

    # Get datapoint
    point_data = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}").json()

    print("Welcome to my weather app")
    print("1. Daily")
    print("2. Hourly")
    print("3. Edit location")
    print("4. Exit")
    while True:
        loc = point_data.get("properties").get("relativeLocation").get("properties")
        print(f"Location: {loc.get("city")}, {loc.get("state")}")

        while True:
            choice = int(input("\nYour input: "))
            if choice == 1:
                show(point_data, "forecast", days)
            elif choice == 2:
                show(point_data, "forecastHourly", hours)
            elif choice == 3:
                latitude = float(input("latitude: "))
                longitude = float(input("longitude: "))
                point_data = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}").json()
                break
            elif choice == 4:
                print("Bye!!!")
                break
        
        if choice == 4:
            break

if __name__ == "__main__":
    main()