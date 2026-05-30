import os
import json
import logging
import numpy as np

logger = logging.getLogger("ClauseGuardConfidence")

WEIGHTS_FILE = ".clauseguard_weights.json"

class ConfidenceCalibrator:
    def __init__(self):
        # Default starting weights
        self.weights = {
            "w_sim": 0.4,
            "w_llm": 0.4,
            "w_hist": 0.2,
            "intercept": 0.0,
            "use_linear": True
        }
        self.load_weights()

    def load_weights(self):
        if os.path.exists(WEIGHTS_FILE):
            try:
                with open(WEIGHTS_FILE, "r") as f:
                    self.weights = json.load(f)
                logger.info("Loaded calibrated confidence weights from disk.")
            except Exception as e:
                logger.warning(f"Failed to load weights: {e}. Using baseline formula.")

    def save_weights(self):
        try:
            with open(WEIGHTS_FILE, "w") as f:
                json.dump(self.weights, f)
            logger.info("Successfully saved calibrated weights to disk.")
        except Exception as e:
            logger.error(f"Error saving weights: {e}")

    def calculate_score(self, cosine_sim: float, llm_conf: float, historical_freq: float = 0.5) -> float:
        """
        Calculates calibrated confidence score.
        Uses logistic sigmoid model if retrained, otherwise falls back to standard weighted formula.
        """
        if self.weights.get("use_linear", True):
            # Baseline: Score = 0.4 * cosine_similarity + 0.4 * llm_confidence + 0.2 * historical_frequency
            score = (self.weights["w_sim"] * cosine_sim + 
                     self.weights["w_llm"] * llm_conf + 
                     self.weights["w_hist"] * historical_freq)
            return float(np.clip(score, 0.0, 1.0))
        else:
            # Logistic Regression probability prediction: 1 / (1 + exp(-(w1*x1 + w2*x2 + w3*x3 + b)))
            z = (self.weights["w_sim"] * cosine_sim + 
                 self.weights["w_llm"] * llm_conf + 
                 self.weights["w_hist"] * historical_freq + 
                 self.weights["intercept"])
            prob = 1.0 / (1.0 + np.exp(-z))
            return float(prob)

    def retrain(self, labeled_pairs: list):
        """
        Trains scikit-learn LogisticRegression classifier on reviewer feedback logs.
        labeled_pairs: list of dicts with keys: cosine_similarity, llm_confidence, historical_frequency, label (0 or 1)
        """
        if len(labeled_pairs) < 10:
            logger.warning(f"Insufficient training examples (have {len(labeled_pairs)}, need at least 10). Skipping retraining.")
            return False
            
        try:
            from sklearn.linear_model import LogisticRegression
            
            # Prepare feature matrices
            X = np.array([[p["cosine_similarity"], p["llm_confidence"], p["historical_frequency"]] for p in labeled_pairs])
            y = np.array([p["label"] for p in labeled_pairs])
            
            # Train Logistic Regression
            clf = LogisticRegression(solver='liblinear')
            clf.fit(X, y)
            
            # Extract weights
            coef = clf.coef_[0]
            intercept = clf.intercept_[0]
            
            self.weights = {
                "w_sim": float(coef[0]),
                "w_llm": float(coef[1]),
                "w_hist": float(coef[2]),
                "intercept": float(intercept),
                "use_linear": False
            }
            self.save_weights()
            logger.info(f"Retrained confidence model successfully. Weights: w_sim={coef[0]:.3f}, w_llm={coef[1]:.3f}, w_hist={coef[2]:.3f}, intercept={intercept:.3f}")
            return True
        except Exception as e:
            logger.error(f"Error during active learning calibration retraining: {e}. Keeping existing weights.")
            return False
