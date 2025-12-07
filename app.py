from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from suggestion_engine import generate_suggestions

app = Flask(__name__)
CORS(app)

OPENWEATHER_KEY = "c16d8edd19f7604faf6b861d8daa3337"


@app.route("/")
def home():
    return {
        "status": "Weather API is running",
        "usage": "/weather?city=New York"
    }


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
        return jsonify({"error": "City not found"}), 404

    # Extract current weather
    description = current["weather"][0]["description"].title()
    temp = current["main"]["temp"]
    feels_like = current["main"]["feels_like"]
    humidity = current["main"]["humidity"]
    pressure = current["main"]["pressure"]
    wind_speed = current["wind"]["speed"]

    # Local time formatting
    local_time = datetime.utcfromtimestamp(current["dt"]).strftime("%Y-%m-%d %H:%M")

    # ---------------------------------------------------
    # 2) FORECAST (3 DAY MIDDAY)
    # ---------------------------------------------------
    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric"
    )

    forecast_raw = requests.get(forecast_url).json()

    forecast_list = []
    days_seen = set()

    for entry in forecast_raw["list"]:
        dt = entry["dt_txt"]  # "2025-12-07 12:00:00"
        date, time = dt.split(" ")

        # Pick data around midday
        if time == "12:00:00" and date not in days_seen:
            forecast_list.append({
                "day": date,
                "temp": entry["main"]["temp"],
                "description": entry["weather"][0]["description"].title()
            })
            days_seen.add(date)

        if len(forecast_list) >= 3:
            break

    # ---------------------------------------------------
    # 3) AI SUGGESTIONS
    # ---------------------------------------------------
    ai_guide = generate_suggestions(
        description=description,
        temp=temp,
        wind_speed=wind_speed
    )

    # ---------------------------------------------------
    # 4) RESPONSE FORMAT
    # ---------------------------------------------------
    result = {
        "city": current["name"],
        "country": current["sys"]["country"],
        "local_time": local_time,
        "temp": temp,
        "feels_like": feels_like,
        "description": description,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,
        "wind_mood": "Windy" if wind_speed > 20 else "Calm",
        "forecast": forecast_list,
        "ai_guide": ai_guide
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
