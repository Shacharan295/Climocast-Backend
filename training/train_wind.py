import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
from xgboost import XGBClassifier
from datetime import datetime

df = pd.read_csv("data/final_weather_dataset.csv")

if "Synthetic" in df["City"].unique():
    df = df[df["City"] != "Synthetic"]

df = df[(df["WindSpeed(km/h)"] >= 0) & (df["WindSpeed(km/h)"] <= 120)]
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df = df.dropna(subset=["Timestamp"])

df = df.sort_values(["City", "Timestamp"])

df["Hour"] = df["Timestamp"].dt.hour
df["Month"] = df["Timestamp"].dt.month

df["WindSpeed_prev"] = df.groupby("City")["WindSpeed(km/h)"].shift(1)
df["WindSpeed_change"] = df.groupby("City")["WindSpeed(km/h)"].diff()
df = df.dropna(subset=["WindSpeed_prev", "WindSpeed_change"])

def wind_category(speed):
    if speed <= 5:
        return "Calm"
    elif speed <= 15:
        return "Breezy"
    elif speed <= 30:
        return "Windy"
    elif speed <= 50:
        return "Strong Wind"
    else:
        return "Storm"

df["WindCategory"] = df["WindSpeed(km/h)"].apply(wind_category)

label_col = "WindCategory"
target_n = 2000

balanced = []
for cls, group in df.groupby(label_col):
    if len(group) >= target_n:
        balanced.append(group.sample(target_n, random_state=42))
    else:
        balanced.append(resample(group, n_samples=target_n, replace=True, random_state=42))

df_bal = pd.concat(balanced)

X = df_bal[[
    "Temp", "Humidity", "Pressure",
    "Clouds(%)", "Visibility(m)",
    "WindDir", "Hour", "Month",
    "WindSpeed_prev", "WindSpeed_change"
]]

y = df_bal["WindCategory"]
le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

model = XGBClassifier(
    n_estimators=600,
    max_depth=10,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="multi:softprob",
    eval_metric="mlogloss"
)

model.fit(X_train, y_train)

version = datetime.now().strftime("%Y%m%d%H%M")
model_path = f"models/wind_category_model_{version}.pkl"
label_path = f"models/wind_category_labels_{version}.pkl"

joblib.dump(model, model_path)
joblib.dump(le, label_path)

accuracy = model.score(X_test, y_test)

with open("models/wind_category_accuracy.txt", "w") as f:
    f.write(f"{model_path}\nAccuracy: {accuracy}\nClasses: {list(le.classes_)}\n")

print("Wind Model Saved →", model_path)
print("Accuracy:", accuracy)
