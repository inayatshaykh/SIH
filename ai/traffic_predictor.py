# ai/traffic_predictor.py
import random

class TrafficPredictor:
    def __init__(self, name=""):
        self.name = name
        self.history = []
        self.current_green_duration = 0

    def train(self):
        print(f"'{self.name}' model is ready (placeholder).")

    def predict_next(self):
        prediction = random.choice(["Low Traffic", "Medium Traffic", "High Traffic"])
        self.history.append(prediction)
        return prediction
