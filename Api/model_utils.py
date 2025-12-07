import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder Api
MODEL_DIR = os.path.join(BASE_DIR, "..", "saved_model")  # ../saved_model


def load_model(model_name="model.pkl"):
    model_path = os.path.join(MODEL_DIR, model_name)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    return joblib.load(model_path)


def load_features(feature_file="features.pkl"):
    feature_path = os.path.join(MODEL_DIR, feature_file)

    if not os.path.exists(feature_path):
        raise FileNotFoundError(f"Feature file not found: {feature_path}")

    return joblib.load(feature_path)