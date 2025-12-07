const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");

const cityNameEl = document.getElementById("city-name");
const countryEl = document.getElementById("country-code");
const localTimeEl = document.getElementById("local-time");
const tempEl = document.getElementById("temp-value");
const conditionTextEl = document.getElementById("condition-text");
const weatherEmojiEl = document.getElementById("weather-emoji");

const feelsLikeEl = document.getElementById("feels-like");
const windEl = document.getElementById("wind");
const humidityEl = document.getElementById("humidity");
const pressureEl = document.getElementById("pressure");
const windMoodTextEl = document.getElementById("wind-mood-text");

const forecastGridEl = document.getElementById("forecast-grid");
const effectsLayer = document.getElementById("weather-effects");

// AI guide elements
const aiSummaryEl = document.getElementById("ai-summary");
const aiMorningEl = document.getElementById("ai-morning");
const aiAfternoonEl = document.getElementById("ai-afternoon");
const aiEveningEl = document.getElementById("ai-evening");
const aiClothingEl = document.getElementById("ai-clothing");
const aiActivitiesEl = document.getElementById("ai-activities");
const aiSafetyEl = document.getElementById("ai-safety");

function formatNumber(value, decimals = 1) {
    const num = Number(value);
    if (isNaN(num)) return "--";
    const d = Math.min(Math.max(decimals, 0), 2);
    return num.toFixed(d);
}

function formatLocalTime(dt, offset) {
    if (dt == null || offset == null) return "--:--";
    const ms = (dt + offset) * 1000;
    const d = new Date(ms);
    const h = d.getUTCHours().toString().padStart(2, "0");
    const m = d.getUTCMinutes().toString().padStart(2, "0");
    return `${h}:${m}`;
}

function categoryToEmoji(cat) {
    const c = (cat || "").toLowerCase();
    if (c === "sunny") return "☀️";
    if (c === "partly cloudy") return "🌤️";
    if (c === "cloudy") return "☁️";
    if (c === "rainy") return "🌧️";
    if (c === "stormy") return "⛈️";
    if (c === "snowy") return "❄️";
    return "🌈";
}

function windMood(speedKmh) {
    const s = Number(speedKmh) || 0;
    if (s < 5) return "Calm 🌬️";
    if (s < 20) return "Breezy 🍃";
    if (s < 40) return "Windy 💨";
    return "Very Windy 💨⚠️";
}

function applyBackground(category) {
    const c = (category || "").toLowerCase();
    let img = "sunny.jpg";

    if (c === "sunny") img = "sunny.jpg";
    else if (c === "partly cloudy") img = "partly_cloudy.jpg";
    else if (c === "cloudy") img = "cloudy.jpg";
    else if (c === "rainy") img = "rainy.jpg";
    else if (c === "stormy") img = "storm.jpg";
    else if (c === "snowy") img = "snow.jpg";

    document.body.style.backgroundImage = `url('/static/images/${img}')`;

    document.body.className = document.body.className
        .split(" ")
        .filter(cl => !cl.startsWith("weather-"))
        .join(" ");
    document.body.classList.add(`weather-${c.replace(" ", "")}`);
}

function createWeatherParticles(category) {
    effectsLayer.innerHTML = "";
    const c = (category || "").toLowerCase();
    let count = 0;
    let type = "";

    if (c === "rainy") {
        count = 40;
        type = "rain";
    } else if (c === "snowy") {
        count = 40;
        type = "snow";
    } else {
        return;
    }

    for (let i = 0; i < count; i++) {
        const span = document.createElement("span");
        span.classList.add("particle", `particle-${type}`);
        span.style.left = Math.random() * 100 + "%";
        span.style.animationDelay = Math.random() * 3 + "s";
        effectsLayer.appendChild(span);
    }
}

function updateUI(data) {
    if (data.error) {
        aiSummaryEl.textContent = data.message || "Error fetching weather.";
        return;
    }

    const category = data.category;
    const emoji = categoryToEmoji(category);

    cityNameEl.textContent = data.city;
    countryEl.textContent = data.country;

    localTimeEl.textContent =
        "Local time: " + formatLocalTime(data.dt, data.timezone);

    tempEl.textContent = formatNumber(data.temp, 1);
    conditionTextEl.textContent = data.condition_text;
    weatherEmojiEl.textContent = emoji;

    feelsLikeEl.textContent = `${formatNumber(data.feels_like, 1)} °C`;
    windEl.textContent = `${formatNumber(data.wind_speed, 1)} km/h`;
    humidityEl.textContent = `${formatNumber(data.humidity, 0)} %`;
    pressureEl.textContent = `${formatNumber(data.pressure, 0)} hPa`;

    const mood = windMood(data.wind_speed);
    windMoodTextEl.textContent = mood;

    // AI guide text
    const g = data.ai_guide || {};
    aiSummaryEl.textContent = g.summary || "";
    aiMorningEl.textContent = g.morning || "";
    aiAfternoonEl.textContent = g.afternoon || "";
    aiEveningEl.textContent = g.evening || "";
    aiClothingEl.textContent = g.clothing || "";
    aiActivitiesEl.textContent = g.activities || "";
    aiSafetyEl.textContent = g.safety || "";

    // forecast cards
    forecastGridEl.innerHTML = "";
    (data.forecast || []).forEach(f => {
        const card = document.createElement("div");
        card.className = "forecast-card";
        const fEmoji = categoryToEmoji(f.condition);
        card.innerHTML = `
            <p>${f.day}</p>
            <p style="font-size:1.4rem;">${fEmoji}</p>
            <p>${formatNumber(f.temp, 1)}°C</p>
            <p style="font-size:0.75rem; opacity:0.85;">${f.condition}</p>
        `;
        forecastGridEl.appendChild(card);
    });

    applyBackground(category);
    createWeatherParticles(category);

    weatherEmojiEl.classList.remove("pop-in");
    void weatherEmojiEl.offsetWidth;
    weatherEmojiEl.classList.add("pop-in");
}

async function fetchWeather(city) {
    if (!city) return;

    const btn = document.getElementById("search-btn");
    const oldText = btn.textContent;
    btn.textContent = "Loading…";
    btn.disabled = true;

    try {
        const res = await fetch("/get_weather", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city })
        });
        const data = await res.json();
        updateUI(data);
    } catch (err) {
        aiSummaryEl.textContent = "Could not load weather. Please try again.";
    } finally {
        btn.textContent = oldText;
        btn.disabled = false;
    }
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    const city = cityInput.value.trim();
    fetchWeather(city);
});

window.addEventListener("load", () => {
    cityInput.value = "London";
    fetchWeather("London");
});
