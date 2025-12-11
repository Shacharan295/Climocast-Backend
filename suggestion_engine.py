import random

# ----------------------------------------
# City / Region Climate Profiles
# ----------------------------------------
CITY_CLIMATE = {
    "mumbai": "coastal humid",
    "chennai": "coastal hot",
    "kolkata": "humid tropical",
    "delhi": "continental dry",
    "new york": "continental cold",
    "london": "cold rainy",
    "tokyo": "temperate mixed",
    "dubai": "desert hot",
    "singapore": "tropical wet",
    "sydney": "coastal mild",
}


def _climate(city, country):
    city_key = (city or "").lower()
    if city_key in CITY_CLIMATE:
        return CITY_CLIMATE[city_key]

    country = (country or "").upper()

    if country in ["NO", "SE", "FI", "RU", "CA"]:
        return "cold northern"
    if country in ["IN", "TH", "MY", "ID"]:
        return "tropical asian"
    if country in ["AE", "SA", "EG"]:
        return "desert hot"
    if country in ["GB", "IE", "DE", "NL"]:
        return "cool european"

    return "generic climate"


# ----------------------------------------
# Temperature Feel
# ----------------------------------------
def _temp_feel(temp, feels_like):
    t = feels_like if feels_like is not None else temp
    if t is None:
        return "moderate"

    if t >= 38: return "extremely hot"
    if t >= 34: return "very hot"
    if t >= 30: return "hot"
    if t >= 24: return "warm"
    if t >= 18: return "mild"
    if t >= 10: return "cool"
    if t >= 0:  return "cold"
    return "freezing"


# ----------------------------------------
# Labels (Humidity / Wind)
# ----------------------------------------
def _humidity_label(h):
    if h is None: return "moderate"
    if h >= 80: return "very humid"
    if h >= 60: return "humid"
    if h <= 30: return "dry"
    return "normal"


def _wind_label(w):
    if w is None: return "calm"
    if w >= 40: return "very windy"
    if w >= 20: return "breezy"
    return "light wind"


# ----------------------------------------
# SAFETY CONCERN (Includes AQI Now)
# ----------------------------------------
def _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi):
    tips = []
    t = temp or 25
    h = humidity or 0
    w = wind_speed_kmh or 0
    cat = (category or "").lower()

    # -------------------------------
    # 🌡 TEMPERATURE RISKS
    # -------------------------------
    if t >= 40:
        tips.append("Extreme heat today — limit outdoor exposure, drink plenty of water, and avoid going out during peak afternoon hours.")
    elif t >= 36:
        tips.append("The heat may feel intense, so stay hydrated and avoid direct sunlight for long periods.")
    elif t <= 0:
        tips.append("Freezing temperatures expected — wear thermal layers and keep skin covered to avoid frostbite.")
    elif t <= 3:
        tips.append("It may feel very cold, so dress in warm layers and reduce time outdoors, especially if the wind increases.")

    # -------------------------------
    # 💧 HUMIDITY RISKS
    # -------------------------------
    if h >= 85 and t >= 30:
        tips.append("High humidity combined with heat can increase discomfort and exhaustion — take regular breaks in cooler areas.")
    elif h >= 80:
        tips.append("Humidity may make the weather feel heavier than usual, so stay hydrated.")

    # -------------------------------
    # 🌬 WIND RISKS
    # -------------------------------
    if w >= 60:
        tips.append("Very strong winds today — avoid tall structures and open areas as gusts may be hazardous.")
    elif w >= 40:
        tips.append("Strong winds can reduce visibility and affect balance, so stay alert if spending time outdoors.")
    elif w >= 25:
        tips.append("Breezy conditions may disrupt lightweight objects outdoors — secure anything on balconies or terraces.")

    # -------------------------------
    # 🌧 RAIN / STORM / SNOW
    # -------------------------------
    if cat in ["rain", "drizzle"]:
        tips.append("Slippery roads and paths are possible, so move carefully and keep rain protection handy.")
    if "thunder" in cat or "storm" in cat:
        tips.append("Thunderstorms expected — stay indoors when possible and avoid open fields or tall isolated trees.")
    if "snow" in cat:
        tips.append("Snow or ice may reduce grip and visibility, so allow extra travel time and move cautiously.")

    # -------------------------------
    # 🏜 CLIMATE-SPECIFIC NOTES
    # -------------------------------
    if climate == "desert hot" and t >= 32:
        tips.append("Dry desert heat can cause dehydration quickly — carry water if you step outside.")
    if climate.startswith("coastal") and ("rain" in cat or "drizzle" in cat or "thunder" in cat):
        tips.append("Coastal showers can form suddenly, so plan longer activities with caution.")

    # -------------------------------
    # 🫁 AIR QUALITY RISKS
    # -------------------------------
    if aqi is not None:
        if aqi == 5:
            tips.append("Air quality is very poor — avoid outdoor activity, keep windows closed, and use a mask if you must go outside.")
        elif aqi == 4:
            tips.append("Air quality is poor today — limit outdoor exercise and consider wearing a mask when going out.")
        elif aqi == 3:
            tips.append("Air quality is moderate — sensitive groups may feel irritation or mild discomfort.")

    # -------------------------------
    # ⚠️ COMBINED RISK INTELLIGENCE
    # -------------------------------
    # ⚡ Heat + Humidity combo = higher risk
    if t >= 35 and h >= 75:
        tips.append("The combination of high heat and humidity can increase heat stress, so rest often and stay hydrated.")

    # ❄ Cold + Wind combo = wind chill risk
    if t <= 5 and w >= 25:
        tips.append("Cold temperatures with wind may cause a stronger chill effect — protect exposed skin.")

    # 🌩 Storm + Wind combo = severe weather
    if ("thunder" in cat or "storm" in cat) and w >= 40:
        tips.append("Stormy and windy conditions together may be dangerous — avoid travel unless necessary.")

    # 🌫 Pollution + Heat = breathing strain
    if aqi >= 4 and t >= 32:
        tips.append("Poor air quality combined with heat can strain breathing — avoid outdoor activity where possible.")

    # -------------------------------
    # DEFAULT SAFE MESSAGE
    # -------------------------------
    if not tips:
        return "No major weather-related concerns today, but staying aware of changing conditions is always helpful."

    return " ".join(tips)



# ----------------------------------------
# Summary Text
# ----------------------------------------
def _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate):

    feel_word = _temp_feel(temp, feels_like)
    hum_label = _humidity_label(humidity)
    wind_label = _wind_label(wind_speed_kmh)
    cat = (category or description or "the weather").lower()

    base_templates = [
        f"In {city}, {country}, the day feels {feel_word} with mostly {cat} conditions.",
        f"{city}, {country} is experiencing a {feel_word} day with {cat} skies.",
        f"Overall, {city} has a {feel_word} feel today with {cat} being the main pattern.",
    ]

    temp_part = f" Around {temp:.1f}°C, it feels close to {feels_like:.1f}°C."
    humidity_part = f" The air is {hum_label}, with about {humidity}% humidity."
    wind_part = f" Winds stay {wind_label}, around {wind_speed_kmh:.1f} km/h."

    climate_extra_map = {
        "coastal humid": " Coastal humidity can make the warmth feel slightly stronger.",
        "tropical wet": " Tropical moisture can add a bit of heaviness to the day.",
        "humid tropical": " The humid air enhances the warmth through the afternoon.",
        "desert hot": " Dry desert warmth often feels sharper during the daytime.",
        "continental cold": " Daytime cold in continental regions can feel crisp and sharp.",
        "cold northern": " Northern daytime temperatures often stay on the cooler side.",
        "cold rainy": " Cloudy or rainy conditions can make the day feel softer and cooler.",
        "cool european": " Cloud cover in such regions usually reduces daytime heating.",
    }

    climate_extra = climate_extra_map.get(climate, "")

    return random.choice(base_templates) + temp_part + humidity_part + wind_part + climate_extra


# ----------------------------------------
# Climate Insight (Max 3 lines)
# ----------------------------------------
def _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate):

    pieces = []
    t = temp or 25
    fl = feels_like or t
    diff = fl - t
    h = humidity or 0
    w = wind_speed_kmh or 0
    p = pressure or 1013
    cat = (category or "").lower()

    # Feels-like
    if diff >= 2:
        pieces.append("It feels a little warmer than the actual temperature, mostly due to local humidity.")
    elif diff <= -2:
        pieces.append("It feels slightly cooler than the reading, helped by wind or lower moisture.")
    else:
        pieces.append("The feels like temperature is almost identical to the actual reading today.")

    # Humidity
    if h >= 80:
        pieces.append("High humidity can make the air feel heavier than usual.")
    elif h <= 30:
        pieces.append("Dry air adds a sharper feel to the temperature.")

    # Pressure
    if p >= 1020:
        pieces.append("Higher pressure usually brings calm and settled weather.")
    elif p <= 1005:
        pieces.append("Lower pressure hints at changing skies or possible light rain.")

    # Wind & Condition Behavior
    if w >= 35:
        pieces.append("Strong winds can lower how the temperature feels, especially in open spaces.")
    if cat in ["rain", "drizzle"]:
        pieces.append("Passing showers may cool the surroundings briefly.")
    if cat in ["clear", "sunny"]:
        pieces.append("Clear skies allow mid-day sunlight to feel stronger.")

    # Climate Insight
    climate_map = {
        "coastal humid": f"{city} often feels heavier in the evenings due to coastal moisture.",
        "desert hot": f"{city} cools down quickly at night despite warm daytime heat.",
        "tropical wet": f"{city} commonly sees quick shifts between sunshine and cloud cover.",
        "humid tropical": f"{city} often alternates between warm and humid spells throughout the day.",
        "tropical asian": f"{city} frequently experiences fast-changing weather patterns.",
        "continental cold": f"{city} cools noticeably after sunset, especially on clearer evenings.",
        "cold northern": f"{city} often develops colder gusts during the night hours.",
        "cold rainy": f"{city} tends to soften in the evening as moisture builds through the day.",
        "cool european": f"{city} loses daytime warmth steadily due to regular cloud cover.",
    }

    pieces.append(climate_map.get(climate, f"Conditions today follow a usual pattern for {city}."))

    text = ". ".join(" ".join(pieces).split(". ")[:3]) + "."
    return text


# ----------------------------------------
# Main Public Function
# ----------------------------------------
def generate_ai_weather_guide(
    city,
    country,
    temp,
    feels_like,
    humidity,
    pressure,
    wind_speed_kmh,
    category,
    description,
    hourly,
    daily,
    timezone_offset,
    aqi=None,   # ⭐ NEW
):
    climate = _climate(city, country)

    return {
        "summary": _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate),
        "safety": _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi),  # ⭐ UPDATED
        "insight": _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate),
    }
