import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

df = pd.read_csv("data/final_weather_dataset.csv")

X = df[[
    "Temp", "Humidity", "Pressure",
    "WindSpeed(km/h)", "Clouds(%)", "Visibility(m)"
]]

y = df["WeatherMain"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=30,
    random_state=42
)

model.fit(X_train, y_train)

version = datetime.now().strftime("%Y%m%d%H%M")
path = f"models/weather_model_{version}.pkl"
labels_path = f"models/weather_labels_{version}.pkl"

joblib.dump(model, path)
joblib.dump(le, labels_path)

accuracy = model.score(X_test, y_test)

with open("models/weather_accuracy.txt", "w") as f:
    f.write(f"{path}\nAccuracy: {accuracy}\nLabels: {list(le.classes_)}\n")

print("Weather Model Saved →", path)
print("Accuracy:", accuracy)
