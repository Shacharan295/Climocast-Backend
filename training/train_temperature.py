import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

df = pd.read_csv("data/final_weather_dataset.csv")

X = df[[
    "MinTemp", "MaxTemp",
    "Humidity", "Pressure",
    "WindSpeed(km/h)", "Clouds(%)", "Visibility(m)"
]]

y = df["Temp"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=350,
    max_depth=20,
    random_state=42
)

model.fit(X_train, y_train)

version = datetime.now().strftime("%Y%m%d%H%M")
path = f"models/temperature_model_{version}.pkl"
joblib.dump(model, path)

accuracy = model.score(X_test, y_test)

with open("models/temperature_accuracy.txt", "w") as f:
    f.write(f"{path}\nAccuracy: {accuracy}\n")

print("Temperature Model Saved →", path)
print("Accuracy:", accuracy)
