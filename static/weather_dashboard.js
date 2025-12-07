/* ============================================================
   AI WEATHER SYSTEM - REAL DATA + CINEMATIC UI SCRIPT
   ============================================================ */

/* ---------- DOM ELEMENTS ---------- */
const backgroundWrapper = document.getElementById("backgroundWrapper");

const cityNameEl = document.getElementById("cityName");
const countryEl = document.getElementById("country");
const localTimeEl = document.getElementById("localTime");
const tempEl = document.getElementById("temperature");
const feelsLikeEl = document.getElementById("feelsLike");
const descEl = document.getElementById("weatherDescription");
const iconEl = document.getElementById("weatherIcon");

const windSpeedEl = document.getElementById("windSpeed");
const humidityEl = document.getElementById("humidity");
const pressureEl = document.getElementById("pressure");
const windMoodEl = document.getElementById("windMood");

const forecastCardsEl = document.getElementById("forecastCards");

const guideMorningEl = document.getElementById("guideMorning");
const guideAfternoonEl = document.getElementById("guideAfternoon");
const guideEveningEl = document.getElementById("guideEvening");
const guideSafetyEl = document.getElementById("guideSafety");

/* ---------- SEARCH ELEMENTS ---------- */
const searchInput = document.getElementById("citySearch");
const searchBtn = document.getElementById("searchBtn");

/* ---------- WEATHER → EMOJI MAPPING ---------- */
function getWeatherEmoji(condition) {
    const c = condition.toLowerCase();
    if (c.includes("clear")) return "☀️";
    if (c.includes("part") || c.includes("few") || c.includes("scattered")) return "⛅";
    if (c.includes("cloud")) return "☁️";
    if (c.includes("rain") || c.includes("drizzle")) return "🌧️";
    if (c.includes("storm") || c.includes("thunder")) return "⛈️";
    if (c.includes("snow")) return "❄️";
    return "🌡️";
}

/* ---------- WIND MOOD ---------- */
function getWindMood(wind) {
    if (wind < 5) return "Calm";
    if (wind < 12) return "Breeze";
    if (wind < 20) return "Windy";
    return "Strong Winds";
}

/* ---------- BACKGROUND SWITCHING ---------- */
function setBackground(condition) {
    const c = condition.toLowerCase();
    let img = "sunny.jpg";

    if (c.includes("clear")) img = "sunny.jpg";
    else if (c.includes("part") || c.includes("few")) img = "partly_cloudy.jpg";
    else if (c.includes("cloud")) img = "cloudy.jpg";
    else if (c.includes("rain") || c.includes("drizzle")) img = "rainy.jpg";
    else if (c.includes("storm") || c.includes("thunder")) img = "storm.jpg";
    else if (c.includes("snow")) img = "snow.jpg";

    backgroundWrapper.style.backgroundImage = `url("/static/images/${img}")`;
}

/* ---------- LOCAL TIME ---------- */
function getLocalTime(dt, timezone) {
    const localMillis = (dt + timezone) * 1000;
    const date = new Date(localMillis);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/* ---------- UPDATE UI ---------- */
function updateUI(data) {
    cityNameEl.textContent = data.city;
    countryEl.textContent = data.country;

    /* Time */
    if (data.dt && data.timezone !== undefined) {
        localTimeEl.textContent = getLocalTime(data.dt, data.timezone);
    } else {
        localTimeEl.textContent = "--:--";
    }

    /* Temperature & Description */
    tempEl.textContent = Math.round(data.temp);
    feelsLikeEl.textContent = Math.round(data.feels_like) + "°C";
    descEl.textContent = data.condition;
    iconEl.textContent = getWeatherEmoji(data.condition);

    /* Metrics */
    windSpeedEl.textContent = data.wind_speed.toFixed(1) + " km/h";
    humidityEl.textContent = data.humidity + "%";
    pressureEl.textContent = data.pressure + " mb";

    /* Wind Mood */
    const mood = getWindMood(data.wind_speed);
    windMoodEl.querySelector(".wind-mood-text").textContent = mood;

    /* Background */
    setBackground(data.condition);

    /* Forecast */
    renderForecast(data.forecast);

    /* AI Guide */
    if (data.ai_guide) {
        guideMorningEl.textContent = data.ai_guide.morning;
        guideAfternoonEl.textContent = data.ai_guide.afternoon;
        guideEveningEl.textContent = data.ai_guide.evening;
        guideSafetyEl.textContent = data.ai_guide.safety;
    }
}

/* ---------- RENDER FORECAST ---------- */
function renderForecast(forecastArr) {
    for (let i = 0; i < 3; i++) {
        const card = document.getElementById(`forecastDay${i}`);
        const emoji = document.getElementById(`forecastEmoji${i}`);
        const temp = document.getElementById(`forecastTemp${i}`);
        const desc = document.getElementById(`forecastDesc${i}`);

        if (forecastArr[i]) {
            card.textContent = forecastArr[i].day;
            emoji.textContent = getWeatherEmoji(forecastArr[i].condition);
            temp.textContent = Math.round(forecastArr[i].temp) + "°C";
            desc.textContent = forecastArr[i].condition;
        }
    }
}

/* ---------- API CALL ---------- */
async function fetchWeather(city) {
    try {
        const res = await fetch("/get_weather", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city })
        });

        const data = await res.json();
        updateUI(data);

    } catch (error) {
        console.error("Weather API error:", error);
        alert("Could not fetch weather data.");
    }
}

/* ---------- SEARCH HANDLER ---------- */
searchBtn.addEventListener("click", () => {
    const city = searchInput.value.trim();
    if (city.length > 0) fetchWeather(city);
});

searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const city = searchInput.value.trim();
        if (city.length > 0) fetchWeather(city);
    }
});

/* ---------- DEFAULT LOAD: LONDON ---------- */
fetchWeather("London");
