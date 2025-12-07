from flask import Flask, request, jsonify
from flask_cors import CORS
from model_utils import load_model, load_features
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for production

# Path folder Api/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ke folder Diamonds/saved_model/
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "saved_model"))

import requests

def download_model_if_missing():
    """Download model.pkl and features.pkl from MODEL_BASE_URL if they are missing.

    Set environment variable MODEL_BASE_URL to the base URL (no trailing slash),
    e.g. https://my-bucket.s3.amazonaws.com/models
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    base_url = os.getenv("MODEL_BASE_URL")
    if not base_url:
        # No external model URL provided; assume model exists in saved_model/
        return

    for fname in ("model.pkl", "features.pkl"):
        outpath = os.path.join(MODEL_DIR, fname)
        if os.path.exists(outpath):
            continue
        url = f"{base_url.rstrip('/')}/{fname}"
        try:
            r = requests.get(url, stream=True, timeout=60)
            r.raise_for_status()
            with open(outpath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded {fname} to {outpath}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")


# Try to download model files if MODEL_BASE_URL is set
download_model_if_missing()

# Load model & features
model = load_model(os.path.join(MODEL_DIR, "model.pkl"))
feature_cols = load_features(os.path.join(MODEL_DIR, "features.pkl"))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        df_input = pd.DataFrame([data])

        # Feature Engineering sesuai model training
        if all(col in df_input.columns for col in ["x", "y", "z"]):
            df_input["volume"] = df_input["x"] * df_input["y"] * df_input["z"]

        drop_cols = ["x", "y", "z", "depth"]
        df_input = df_input.drop(columns=[c for c in drop_cols if c in df_input.columns])

        # ===============================
        #   ENCODING KATEGORICAL
        # ===============================

        cut_map = {
            "Fair": 1,
            "Good": 2,
            "Very Good": 3,
            "Premium": 4,
            "Ideal": 5
        }

        color_map = {
            "D": 1,
            "E": 2,
            "F": 3,
            "G": 4,
            "H": 5,
            "I": 6,
            "J": 7
        }

        clarity_map = {
            "IF": 1,
            "VVS1": 2,
            "VVS2": 3,
            "VS1": 4,
            "VS2": 5,
            "SI1": 6,
            "SI2": 7,
            "I1": 8
        }

        if "cut" in df_input:
            df_input["cut"] = df_input["cut"].map(cut_map)

        if "color" in df_input:
            df_input["color"] = df_input["color"].map(color_map)

        if "clarity" in df_input:
            df_input["clarity"] = df_input["clarity"].map(clarity_map)

        # ===============================
        #   END ENCODING
        # ===============================

        # Urutan must match feature_cols
        df_input = df_input[feature_cols]

        prediction = model.predict(df_input)[0]

        return jsonify({
            "input": data,
            "predicted_price": float(prediction)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)