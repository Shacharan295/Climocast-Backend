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
# Labels
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
# SAFETY CONCERN
# ----------------------------------------
def _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi):
    tips = []
    t = temp or 25
    h = humidity or 0
    w = wind_speed_kmh or 0
    cat = (category or "").lower()

    # Temperature
    if t >= 40:
        tips.append("Extreme heat dominates the day. Limit outdoor exposure, drink water often, and avoid peak afternoon hours.")
    elif t >= 36:
        tips.append("Intense heat lingers today. Stay hydrated and reduce long periods under direct sunlight.")
    elif t <= 0:
        tips.append("Freezing conditions are present. Wear thermal layers and protect exposed skin to prevent frostbite.")
    elif t <= 3:
        tips.append("The cold may feel biting today. Dress warmly and limit time outdoors, especially as winds increase.")

    # Humidity
    if h >= 85 and t >= 30:
        tips.append("High humidity intensifies the heat and increases fatigue. Take regular breaks in cooler areas.")
    elif h >= 80:
        tips.append("Moist air may feel heavy and uncomfortable, so staying hydrated is important.")

    # Wind
    if w >= 60:
        tips.append("Very strong winds are possible. Avoid open spaces and stay alert to sudden gusts.")
    elif w >= 40:
        tips.append("Strong winds may affect balance and visibility, so remain cautious outdoors.")
    elif w >= 25:
        tips.append("Breezy conditions can shift lightweight objects. Secure items on balconies or terraces.")

    # Rain Storm Snow
    if cat in ["rain", "drizzle"]:
        tips.append("Wet roads and walkways may become slippery, so move carefully and carry rain protection.")
    if "thunder" in cat or "storm" in cat:
        tips.append("Storm activity is expected. Staying indoors is the safer choice, away from open areas.")
    if "snow" in cat:
        tips.append("Snow and ice can reduce grip and visibility. Allow extra travel time and walk cautiously.")

    # Climate specific
    if climate == "desert hot" and t >= 32:
        tips.append("Dry desert heat can cause dehydration quickly, so carry water when stepping outside.")
    if climate.startswith("coastal") and ("rain" in cat or "drizzle" in cat or "thunder" in cat):
        tips.append("Coastal weather can change suddenly, so plan outdoor activities with care.")

    # Air quality
    if aqi is not None:
        if aqi == 5:
            tips.append("Air quality is very poor. Stay indoors, keep windows closed, and wear a mask if you must go out.")
        elif aqi == 4:
            tips.append("Air quality is poor today. Limit outdoor activity and consider using a mask.")
        elif aqi == 3:
            tips.append("Air quality is moderate. Sensitive individuals may feel mild irritation.")

    # Combined risks
    if t >= 35 and h >= 75:
        tips.append("Heat combined with humidity can raise heat stress. Rest often and hydrate well.")
    if t <= 5 and w >= 25:
        tips.append("Cold air mixed with wind increases chill. Protect exposed skin.")
    if ("thunder" in cat or "storm" in cat) and w >= 40:
        tips.append("Stormy and windy conditions together can be dangerous. Avoid unnecessary travel.")
    if aqi >= 4 and t >= 32:
        tips.append("Poor air quality combined with heat can strain breathing. Reduce outdoor exposure.")

    if not tips:
        return "No major weather related concerns today. Staying aware of changing conditions is still a good idea."

    return " ".join(tips)


# ----------------------------------------
# SUMMARY
# ----------------------------------------
def _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate):

    feel_word = _temp_feel(temp, feels_like)
    hum_label = _humidity_label(humidity)
    wind_label = _wind_label(wind_speed_kmh)
    cat = (category or description or "the weather").lower()

    base_templates = [
        f"In {city}, {country}, the day unfolds with a {feel_word} tone under mostly {cat} skies.",
        f"{city}, {country} experiences a distinctly {feel_word} day shaped by prevailing {cat} conditions.",
        f"Today in {city}, a {feel_word} atmosphere sets the mood as {cat} patterns dominate.",
    ]

    temp_part = f" Around {temp:.1f}°C, it feels closer to {feels_like:.1f}°C."
    humidity_part = f" The air is {hum_label}, with humidity near {humidity}%."
    wind_part = f" Winds remain {wind_label}, reaching about {wind_speed_kmh:.1f} km per hour."

    climate_extra_map = {
        "coastal humid": " Coastal moisture can make the air feel heavier through the day.",
        "tropical wet": " Tropical humidity adds a lingering heaviness to the atmosphere.",
        "humid tropical": " Humid air enhances warmth across the afternoon.",
        "desert hot": " Dry desert warmth often feels sharp under direct sunlight.",
        "continental cold": " Continental cold brings a crisp and penetrating daytime chill.",
        "cold northern": " Northern regions often maintain cooler temperatures throughout the day.",
        "cold rainy": " Cloudy and rainy skies soften temperatures but deepen the chill.",
        "cool european": " Frequent cloud cover limits daytime heating.",
    }

    return random.choice(base_templates) + temp_part + humidity_part + wind_part + climate_extra_map.get(climate, "")


# ----------------------------------------
# CLIMATE INSIGHT
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

    if diff >= 2:
        pieces.append("The air feels warmer than the thermometer suggests, influenced by local humidity.")
    elif diff <= -2:
        pieces.append("Temperatures feel cooler than measured due to wind movement or drier air.")
    else:
        pieces.append("The perceived temperature closely matches the actual reading today.")

    if h >= 80:
        pieces.append("High humidity gives the air a heavier and slower feel.")
    elif h <= 30:
        pieces.append("Dry air sharpens the sensation of temperature.")

    if p >= 1020:
        pieces.append("High pressure supports calmer and more settled weather.")
    elif p <= 1005:
        pieces.append("Lower pressure points to shifting skies or unsettled conditions.")

    if w >= 35:
        pieces.append("Stronger winds can lower how warm or cold it feels, especially in open areas.")
    if cat in ["rain", "drizzle"]:
        pieces.append("Passing showers can briefly cool the surroundings.")
    if cat in ["clear", "sunny"]:
        pieces.append("Clear skies allow sunlight to feel more intense during mid day.")

    climate_map = {
        "coastal humid": f"{city} often feels heavier toward evening due to coastal moisture.",
        "desert hot": f"{city} cools quickly after sunset despite warm daytime heat.",
        "tropical wet": f"{city} frequently shifts between sunshine and cloud cover.",
        "humid tropical": f"{city} moves between warm and humid spells through the day.",
        "tropical asian": f"{city} experiences fast changing weather patterns.",
        "continental cold": f"{city} cools noticeably after sunset, especially on clear evenings.",
        "cold northern": f"{city} often sees colder gusts developing overnight.",
        "cold rainy": f"{city} gradually softens as moisture builds later in the day.",
        "cool european": f"{city} steadily loses warmth due to persistent cloud cover.",
    }

    pieces.append(climate_map.get(climate, f"Conditions today follow a familiar pattern for {city}."))

    return ". ".join(" ".join(pieces).split(". ")[:3]) + "."


# ----------------------------------------
# MAIN FUNCTION
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
    aqi=None,
):
    climate = _climate(city, country)

    return {
        "summary": _build_summary_text(city, country, temp, feels_like, humidity, wind_speed_kmh, category, description, climate),
        "safety": _build_safety_text(temp, humidity, wind_speed_kmh, category, climate, aqi),
        "insight": _build_insight_text(city, country, temp, feels_like, humidity, pressure, wind_speed_kmh, category, climate),
    }
