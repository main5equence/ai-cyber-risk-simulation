import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib
import os


MODEL_PATH = "ml_model.pkl"


class CyberRiskMLModel:
    def __init__(self, random_state: int = 42):
        self.model = MultiOutputRegressor(
            RandomForestRegressor(
                n_estimators=30,
                max_depth=5,
                random_state=random_state,
            )
        )
        self.is_trained = False

    def save(self):
        joblib.dump(self.model, MODEL_PATH)

    def load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model file not found. Run training first.")

        self.model = joblib.load(MODEL_PATH)
        self.is_trained = True

    def generate_synthetic_data(self, n_samples: int = 500):
        X = []
        y = []

        for _ in range(n_samples):
            risk_score = np.random.uniform(0.05, 1.0)
            detection = np.random.uniform(0.0, 1.0)
            response = np.random.uniform(0.0, 1.0)

            prob_multiplier = np.random.uniform(0.4, 1.3)
            base_mean_loss = np.random.uniform(30000, 500000)
            base_std_loss = base_mean_loss * np.random.uniform(0.15, 0.40)

            attack_prob = min(risk_score * prob_multiplier, 0.95)

            severity_factor = 1.0 - (detection * 0.30) - (response * 0.20)
            severity_factor = max(severity_factor, 0.35)

            mean_loss = base_mean_loss * severity_factor

            std_factor = 1.0 - (response * 0.25)
            std_factor = max(std_factor, 0.50)
            std_loss = base_std_loss * std_factor

            X.append([
                risk_score,
                detection,
                response,
                prob_multiplier,
                base_mean_loss,
                base_std_loss,
            ])
            y.append([attack_prob, mean_loss, std_loss])

        return np.array(X), np.array(y)

    def train(self):
        X, y = self.generate_synthetic_data()
        self.model.fit(X, y)
        self.is_trained = True

    def predict_risk_parameters(
        self,
        risk_score,
        detection,
        response,
        prob_multiplier,
        base_mean_loss,
        base_std_loss,
    ):
        if not self.is_trained:
            raise ValueError("Model not trained")

        X = np.array([[
            risk_score,
            detection,
            response,
            prob_multiplier,
            base_mean_loss,
            base_std_loss,
        ]])

        pred = self.model.predict(X)[0]

        return {
            "attack_prob": float(np.clip(pred[0], 0.01, 0.95)),
            "mean_loss": float(max(pred[1], 1000)),
            "std_loss": float(max(pred[2], 500)),
        }
    