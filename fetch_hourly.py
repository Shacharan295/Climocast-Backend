import requests
import csv
import time
from datetime import datetime
from data.cities_list import cities

api_key = "c16d8edd19f7604faf6b861d8daa3337"
csv_file = "data/weather_dataset_live.csv"

# Create CSV with header if not exists
try:
    with open(csv_file, 'x', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "City", "Country", "Timestamp",
            "Temp", "MinTemp", "MaxTemp",
            "Humidity", "Pressure",
            "WindSpeed(km/h)", "WindDir",
            "Clouds(%)", "Visibility(m)",
            "WeatherMain", "WeatherDescription"
        ])
except FileExistsError:
    pass


def save_city_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != 200:
        print(f"City not found: {city}")
        return

    main = res["main"]
    wind = res.get("wind", {})
    weather = res["weather"][0]

    wind_speed_kmh = round(wind.get("speed", 0) * 3.6, 2)

    row = [
        res["name"],
        res["sys"]["country"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        main.get("temp", 0),
        main.get("temp_min", 0),
        main.get("temp_max", 0),
        main.get("humidity", 0),
        main.get("pressure", 0),

        wind_speed_kmh,
        wind.get("deg", 0),

        res.get("clouds", {}).get("all", 0),
        res.get("visibility", 0),

        weather.get("main", "Unknown"),
        weather.get("description", "Unknown")
    ]

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print(f"Saved weather → {res['name']}, {res['sys']['country']}")


for city in cities:
    save_city_weather(city)
    time.sleep(1)
