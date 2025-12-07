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