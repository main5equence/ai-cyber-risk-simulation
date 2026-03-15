import numpy as np


ATTACK_TYPES = {
    "Phishing": {"prob_multiplier": 1.20, "mean": 40000, "std": 12000},
    "Ransomware": {"prob_multiplier": 0.70, "mean": 250000, "std": 70000},
    "Data Breach": {"prob_multiplier": 0.45, "mean": 450000, "std": 120000},
    "Insider Threat": {"prob_multiplier": 0.55, "mean": 160000, "std": 50000},
}


def simulate_attack_event(base_prob, detection, response, mean_loss, std_loss):
    """
    Simulates one attack type in one year.
    Returns loss for that attack type.
    """

    attack_happens = np.random.rand() < base_prob

    if not attack_happens:
        return 0.0

    loss = np.random.normal(mean_loss, std_loss)
    loss = max(loss, 0.0)

    detected = np.random.rand() < detection
    if detected:
        loss *= 0.55

    response_factor = 1.0 - (response * 0.45)
    loss *= response_factor

    return float(max(loss, 0.0))


def simulate_year(risk_score, detection, response):
    """
    Simulates one year of cyber losses across multiple attack types.
    Returns total annual loss.
    """

    total_loss = 0.0

    for _, params in ATTACK_TYPES.items():
        attack_prob = min(risk_score * params["prob_multiplier"], 0.95)

        total_loss += simulate_attack_event(
            base_prob=attack_prob,
            detection=detection,
            response=response,
            mean_loss=params["mean"],
            std_loss=params["std"],
        )

    return float(total_loss)


def simulate_losses(risk_score, detection, response, n_simulations=3000):
    """
    Monte Carlo simulation of annual losses.
    """

    losses = [
        simulate_year(risk_score, detection, response)
        for _ in range(n_simulations)
    ]
    return np.array(losses, dtype=float)
