import numpy as np


def calculate_risk(training, detection, response, incidents):
    """
    Calculates normalized cyber risk score in range 0.05-0.95.
    Higher value = higher cyber risk.
    """

    base_risk = 0.55

    risk = base_risk
    risk -= training * 0.20
    risk -= detection * 0.25
    risk -= response * 0.20
    risk += incidents * 0.03

    return float(np.clip(risk, 0.05, 0.95))
