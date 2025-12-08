# suggestion_engine.py — CITY-AWARE + HIGH VARIATION EDITION

import random

# -----------------------------
# City Climate Profiles
# -----------------------------
CITY_CLIMATE = {
    "mumbai": "coastal-humid",
    "chennai": "coastal-hot",
    "kolkata": "humid-tropical",
    "delhi": "continental-extreme",
    "new york": "continental-cold",
    "london": "cold-rainy",
    "tokyo": "temperate-mixed",
    "dubai": "desert-hot",
    "singapore": "tropical-wet",
    "sydney": "coastal-mild",
}

def _climate(city):
    return CITY_CLIMATE.get(city.lower(), "generic")


# -----------------------------
# Temperature Feel
# -----------------------------
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


# -----------------------------
# Clothing Advice with CITY VARIATION
# -----------------------------
def _clothing_advice(temp, category, wind_speed, humidity, climate):
    t = temp if temp is not None else 25
    cat = (category or "").lower()

    coastal_bonus = " Since it's a coastal region, humidity may make clothes feel heavier."
    desert_bonus = " The dry desert air may feel harsh, so cover exposed skin."
    cold_country_bonus = " Winters here drop quickly, so warm layers help a lot."

    base = ""

    if climate == "coastal-humid" and t >= 28:
        base = "Stick to very light fabrics; humidity may make the heat feel stronger."
    elif climate == "desert-hot":
        base = "Go for loose, full-sleeve cotton to avoid harsh sun exposure."
    elif climate == "cold-rainy":
        base = "A warm waterproof jacket is useful because rain can start anytime."
    elif climate == "continental-cold" and t <= 10:
        base = "Layer up well, especially during wind gusts typical to this region."

    if t >= 35:
        advice = "Wear ultra-light cotton, sunglasses, and stay shaded."
    elif t >= 28:
        advice = "Light cotton and breathable clothes feel best today."
    elif t >= 22:
        advice = "Comfortable T-shirt and jeans are fine. A thin waterproof layer if rain pops up."
    elif t >= 15:
        advice = "A light jacket will help especially when the wind picks up."
    elif t >= 5:
        advice = "Warm sweaters and a light coat are recommended."
    else:
        advice = "Use a proper winter jacket, gloves, and warm layers."

    climate_tail = ""
    if "coastal" in climate: climate_tail = coastal_bonus
    if "desert" in climate: climate_tail = desert_bonus
    if "continental-cold" == climate: climate_tail = cold_country_bonus

    return advice + climate_tail


# -----------------------------
# Activity Advice with CITY VARIATION
# -----------------------------
def _activity_advice(category, temp, wind_speed, humidity, climate):
    cat = (category or "").lower()
    t = temp if temp else 25
    w = wind_speed or 0
    h = humidity or 0

    if cat == "stormy":
        return "Strong winds and rain expected. Stick to indoor activities."
    if cat == "rainy":
        return "Short walks are fine with an umbrella; indoor cafés and malls feel nicer."
    if cat == "snowy":
        return "Walking in snow is enjoyable if roads are safe. Avoid long outdoor travel."

    climate_bonus = ""
    if climate == "coastal-humid" and h > 70:
        climate_bonus = " Coastal humidity may make long outdoor activity feel tiring."
    elif climate == "desert-hot" and t > 34:
        climate_bonus = " Desert heat is harsh; limit activity during peak afternoon."
    elif climate == "cold-rainy" and t < 12:
        climate_bonus = " Cold rain may appear unexpectedly, so stay near shelter."

    if t >= 36:
        return "Prefer shaded or indoor plans; heat is intense." + climate_bonus
    if w >= 35:
        return "Windy day—pick sheltered spots." + climate_bonus
    if h >= 80 and t > 28:
        return "High humidity may reduce comfort, choose lighter activities." + climate_bonus

    return "A good day for normal outdoor plans — walks, small trips, or meeting friends." + climate_bonus


# -----------------------------
# Safety Advice with CITY VARIATION
# -----------------------------
def _safety_advice(temp, humidity, wind_speed, category, climate):
    tips = []
    t = temp or 25
    h = humidity or 0
    w = wind_speed or 0
    cat = (category or "").lower()

    if t >= 36:
        tips.append("Stay hydrated and avoid long exposure to the sun.")
    if t <= 5:
        tips.append("Wear strong winter layers to avoid cold stress.")
    if h >= 80:
        tips.append("High humidity may cause discomfort; take breaks in cool areas.")
    if w >= 40:
        tips.append("Strong winds—avoid open areas and secure loose objects.")
    if cat in ["rainy", "stormy"]:
        tips.append("Roads may be slippery. Travel carefully.")

    # climate-specific warnings
    if climate == "desert-hot" and t > 34:
        tips.append("Dry air may cause dehydration quickly—carry enough water.")
    if climate.startswith("coastal") and cat == "rainy":
        tips.append("Coastal areas may experience sudden rain bursts.")

    if not tips:
        return "No major safety concerns today."

    return " ".join(tips)


# -----------------------------
# Time Blocks (kept simple but can expand)
# -----------------------------
def _time_block_text(name, feel_word, category, climate):
    cat = (category or "").lower()
    f = feel_word
    variations = {
        "morning": [
            f"Morning starts {f} with {cat} conditions.",
            f"A {f} morning with a calm start.",
            f"Morning feels {f}; a good time for a short walk.",
        ],
        "afternoon": [
            f"Afternoon turns {f} and you may notice stronger light.",
            f"A {f} afternoon; plan your main activities now.",
            f"Afternoon stays {f} with steady weather.",
        ],
        "evening": [
            f"Evening becomes slightly cooler and feels {f}.",
            f"A calm {f} evening—ideal for relaxing outdoors.",
            f"Evening stays {f} with mild winds.",
        ],
    }
    return random.choice(variations[name])


# -----------------------------
# MAIN ENGINE
# -----------------------------
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
):
    climate = _climate(city)
    feel_word = _temp_feel(temp, feels_like)
    cat = category or description or "the weather"

    summary = (
        f"In {city}, {country}, the weather feels {feel_word} with {cat.lower()} skies. "
        f"Temperature is around {temp:.1f}°C (feels like {feels_like:.1f}°C), "
        f"humidity near {humidity}%, and winds around {wind_speed_kmh:.1f} km/h."
    )

    morning_text = _time_block_text("morning", feel_word, cat, climate)
    afternoon_text = _time_block_text("afternoon", feel_word, cat, climate)
    evening_text = _time_block_text("evening", feel_word, cat, climate)

    clothing_text = _clothing_advice(temp, category, wind_speed_kmh, humidity, climate)
    activity_text = _activity_advice(category, temp, wind_speed_kmh, humidity, climate)
    safety_text = _safety_advice(temp, humidity, wind_speed_kmh, category, climate)

    insight_text = (
        f"Overall, {city} experiences {feel_word} conditions today. "
        f"As a {climate.replace('-', ' ')} region, weather patterns shift slightly, "
        f"but no unusual trends are expected."
    )

    return {
        "summary": summary,
        "morning": morning_text,
        "afternoon": afternoon_text,
        "evening": evening_text,
        "clothing": clothing_text,
        "activities": activity_text,
        "safety": safety_text,
        "insight": insight_text,
    }
