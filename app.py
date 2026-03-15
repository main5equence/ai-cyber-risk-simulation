import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from risk_model import calculate_risk
from attack_simulation import simulate_losses, ATTACK_TYPES
from optimizer import evaluate_strategy


st.set_page_config(
    page_title="AI Cyber Risk Decision Platform",
    page_icon="🛡️",
    layout="wide",
)

st.title("AI Cyber Risk Decision Platform")
st.caption("Interactive dashboard for cyber risk analysis, loss simulation, and investment strategy optimization.")

# Sidebar inputs
st.sidebar.header("Company Security Profile")

training = st.sidebar.slider("Security Training", 0.0, 1.0, 0.40, 0.01)
detection = st.sidebar.slider("Threat Detection", 0.0, 1.0, 0.50, 0.01)
response = st.sidebar.slider("Incident Response", 0.0, 1.0, 0.50, 0.01)
incidents = st.sidebar.slider("Incidents Last Year", 0, 20, 3, 1)

run = st.button("Run Analysis", type="primary")

if run:
    risk = calculate_risk(training, detection, response, incidents)

    losses = simulate_losses(
        risk_score=risk,
        detection=detection,
        response=response,
        n_simulations=4000,
    )

    expected_loss = float(np.mean(losses))
    median_loss = float(np.median(losses))
    var_95 = float(np.percentile(losses, 95))
    worst_5 = losses[losses >= var_95]
    cvar_95 = float(np.mean(worst_5)) if len(worst_5) > 0 else var_95

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cyber Risk Score", f"{risk:.2f}")
    col2.metric("Expected Annual Loss", f"${expected_loss:,.0f}")
    col3.metric("VaR 95%", f"${var_95:,.0f}")
    col4.metric("CVaR 95%", f"${cvar_95:,.0f}")

    # Gauge chart
    st.subheader("Risk Gauge")
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk * 100,
            title={"text": "Cyber Risk Level"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"thickness": 0.25},
                "steps": [
                    {"range": [0, 33], "color": "#1f7a1f"},
                    {"range": [33, 66], "color": "#d4a017"},
                    {"range": [66, 100], "color": "#b22222"},
                ],
            },
        )
    )
    gauge_fig.update_layout(height=320)
    st.plotly_chart(gauge_fig, use_container_width=True)

    # Loss distribution
    st.subheader("Cyber Loss Distribution")
    hist_fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(losses, bins=40)
    ax.set_title("Monte Carlo Distribution of Annual Cyber Losses")
    ax.set_xlabel("Annual Loss")
    ax.set_ylabel("Frequency")
    st.pyplot(hist_fig)

    # Heatmap
    st.subheader("Cyber Risk Heatmap")
    train_values = np.linspace(0.0, 1.0, 11)
    detect_values = np.linspace(0.0, 1.0, 11)

    heatmap_data = []
    for t in train_values:
        row = []
        for d in detect_values:
            row.append(calculate_risk(t, d, response, incidents))
        heatmap_data.append(row)

    heatmap_df = pd.DataFrame(
        heatmap_data,
        index=[round(v, 2) for v in train_values],
        columns=[round(v, 2) for v in detect_values],
    )

    heatmap_fig = px.imshow(
        heatmap_df,
        labels=dict(x="Threat Detection", y="Security Training", color="Risk"),
        aspect="auto",
        title="Risk Heatmap: Training vs Detection",
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

    # Attack exposure
    st.subheader("Attack Exposure by Scenario")
    exposure_rows = []
    for attack_name, params in ATTACK_TYPES.items():
        scenario_probability = min(risk * params["prob_multiplier"], 0.95)
        exposure_rows.append(
            {
                "Attack Type": attack_name,
                "Probability": scenario_probability,
                "Expected Severity": params["mean"],
            }
        )

    exposure_df = pd.DataFrame(exposure_rows)

    exposure_fig = px.bar(
        exposure_df,
        x="Attack Type",
        y="Probability",
        title="Estimated Attack Probability by Type",
    )
    st.plotly_chart(exposure_fig, use_container_width=True)

    # Strategy optimizer
    st.subheader("AI Investment Strategy Optimizer")
    strategy_results = evaluate_strategy(base_incidents=incidents, n_simulations=2000)
    strategy_df = pd.DataFrame(strategy_results)

    best_strategy = strategy_df.iloc[0]

    st.success(
        f"Recommended strategy: **{best_strategy['Strategy']}** "
        f"(Total Cost: ${best_strategy['Total Cost']:,.0f})"
    )

    st.dataframe(strategy_df, use_container_width=True)

    strategy_fig = px.bar(
        strategy_df,
        x="Strategy",
        y="Total Cost",
        title="Total Cost by Cybersecurity Strategy",
    )
    st.plotly_chart(strategy_fig, use_container_width=True)

    # Recommendation text
    st.subheader("Executive Recommendation")

    recommendations = []

    if training < 0.5:
        recommendations.append("- Increase employee cyber awareness and phishing training.")
    if detection < 0.6:
        recommendations.append("- Improve detection stack: SIEM, EDR/XDR, alert triage, monitoring.")
    if response < 0.6:
        recommendations.append("- Strengthen incident response playbooks and recovery procedures.")
    if incidents >= 5:
        recommendations.append("- High incident history suggests elevated residual cyber exposure.")

    if not recommendations:
        recommendations.append("- Current security posture is relatively mature; focus on continuous optimization.")

    st.markdown("\n".join(recommendations))

else:
    st.info("Set the company profile in the sidebar and click **Run Analysis**.")

    