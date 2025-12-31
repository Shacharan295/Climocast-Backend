from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from suggestion_engine import generate_ai_weather_guide
from city_fuzzy import get_city_suggestions

app = Flask(__name__)
CORS(app)

OPENWEATHER_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}, 200


@app.route("/")
def home():
    return {"status": "Weather API running"}


# -------------------------------
# CITY SUGGESTIONS
# -------------------------------
@app.route("/suggest")
def suggest_city():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"query": "", "suggestions": []})

    suggestions = get_city_suggestions(query, limit=5)
    return jsonify({"query": query, "suggestions": suggestions})


# -------------------------------
# AQI HELPERS (REAL AQI)
# -------------------------------
def calculate_aqi_pm25(pm25):
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]

    for c_low, c_high, aqi_low, aqi_high in breakpoints:
        if c_low <= pm25 <= c_high:
            return round(
                ((aqi_high - aqi_low) / (c_high - c_low))
                * (pm25 - c_low)
                + aqi_low
            )
    return None


def aqi_label(aqi):
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# -------------------------------
# WEATHER ENDPOINT
# -------------------------------
@app.route("/weather")
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City is required"}), 400

    # -------------------------------
    # 1) CURRENT WEATHER
    # -------------------------------
    current_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={OPENWEATHER_KEY}&units=metric"
    )
    current = requests.get(current_url).json()

    if current.get("cod") != 200:
        return jsonify({
            "error": "city_not_found",
            "suggestions": get_city_suggestions(city)
        })

    description = current["weather"][0]["description"].title()
    category = current["weather"][0]["main"]

    temp = current["main"]["temp"]
    feels_like = current["main"]["feels_like"]
    humidity = current["main"]["humidity"]
    pressure = current["main"]["pressure"]

    wind_speed = current["wind"]["speed"] * 3.6
    timezone_offset = current["timezone"]

    local_time = datetime.utcfromtimestamp(
        current["dt"] + timezone_offset
    ).strftime("%Y-%m-%d %H:%M")

    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    # -------------------------------
    # 2) FORECAST FETCH
    # -------------------------------
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
    )
    forecast_raw = requests.get(forecast_url).json()

    # -------------------------------
    # ⭐ ONLY FIX: ROUND CURRENT TIME TO 3-HOUR BLOCK
    # -------------------------------
    hourly_temps = []

    

    count = 0
    for entry in forecast_raw.get("list", []):
        if count > 7:
            break
        hourly_temps.append({
            "dt": entry["dt"],
            "temp": entry["main"]["temp"]
        })
        count += 1

    # -------------------------------
    # DAILY FORECAST (UNCHANGED)
    # -------------------------------
    forecast_list = []
    days_seen = set()

    for entry in forecast_raw.get("list", []):
        date, time = entry["dt_txt"].split(" ")
        if time == "12:00:00" and date not in days_seen:
            forecast_list.append({
                "day": date,
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"].title()
            })
            days_seen.add(date)
        if len(forecast_list) >= 3:
            break

    # -------------------------------
    # 4) AIR QUALITY (REAL AQI)
    # -------------------------------
    aqi_url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}"
    )
    aqi_raw = requests.get(aqi_url).json()

    components = aqi_raw.get("list", [{}])[0].get("components", {})
    pm25 = components.get("pm2_5")

    real_aqi = calculate_aqi_pm25(pm25)
    real_aqi_label = aqi_label(real_aqi)

    # -------------------------------
    # 5) AI WEATHER GUIDE
    # -------------------------------
    ai_guide = generate_ai_weather_guide(
        city=current["name"],
        country=current["sys"]["country"],
        temp=temp,
        feels_like=feels_like,
        humidity=humidity,
        pressure=pressure,
        wind_speed_kmh=wind_speed,
        category=category,
        description=description,
        hourly=hourly_temps,
        daily=forecast_list,
        timezone_offset=timezone_offset,
        aqi=real_aqi,
    )

    def get_wind_mood(speed):
        if speed <= 5:
            return "Calm"
        elif speed <= 15:
            return "Light Breeze"
        elif speed <= 25:
            return "Breezy"
        elif speed <= 40:
            return "Windy"
        elif speed <= 60:
            return "Very Windy"
        else:
            return "Storm Winds"

    return jsonify({
        "city": current["name"],
        "country": current["sys"]["country"],
        "local_time": local_time,
        "temp": temp,
        "feels_like": feels_like,
        "description": description,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": round(wind_speed, 1),
        "wind_mood": get_wind_mood(wind_speed),
        "air_quality": {
            "aqi": real_aqi,
            "label": real_aqi_label,
            "pm25": pm25
        },
        "forecast": forecast_list,
        "hourly": hourly_temps,
        "timezone_offset": timezone_offset,
        "ai_guide": ai_guide
    })


if __name__ == "__main__":
    app.run(debug=True)
