import numpy as np
from attack_simulation import simulate_losses


STRATEGIES = [
    ("Cost Efficient", (0.35, 0.45, 0.40), 40000),
    ("Balanced", (0.55, 0.60, 0.60), 70000),
    ("Detection Focus", (0.45, 0.80, 0.60), 85000),
    ("Resilience Focus", (0.55, 0.60, 0.85), 90000),
    ("Zero Trust Plus", (0.75, 0.80, 0.80), 120000),
]


def evaluate_strategy(base_incidents, n_simulations=2000):
    """
    Evaluates each strategy:
    - calculates risk score internally
    - simulates expected annual loss
    - adds implementation cost
    - returns total cost and recommendation ranking
    """

    from risk_model import calculate_risk

    results = []

    for strategy_name, controls, investment_cost in STRATEGIES:
        training, detection, response = controls

        risk = calculate_risk(
            training=training,
            detection=detection,
            response=response,
            incidents=base_incidents,
        )

        losses = simulate_losses(
            risk_score=risk,
            detection=detection,
            response=response,
            n_simulations=n_simulations,
        )

        expected_loss = float(np.mean(losses))
        total_cost = expected_loss + investment_cost

        results.append(
            {
                "Strategy": strategy_name,
                "Training": training,
                "Detection": detection,
                "Response": response,
                "Investment Cost": investment_cost,
                "Risk Score": round(risk, 3),
                "Expected Loss": round(expected_loss, 2),
                "Total Cost": round(total_cost, 2),
            }
        )

    results = sorted(results, key=lambda x: x["Total Cost"])
    return results
