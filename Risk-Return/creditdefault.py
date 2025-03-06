import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import shap

# Define credit score factors
factors = {
    'Payment History': {'impact': 1, 'weight': 0.15},
    'Credit Mix': {'impact': 1, 'weight': 0.10},
    'Length of Credit History': {'impact': 1, 'weight': 0.10},
    'Credit Utilization (keep below 30%)': {'impact': 1, 'weight': 0.10},
    'Total Accounts in Good Standing': {'impact': 1, 'weight': 0.10},
    'Loan Payment History': {'impact': 1, 'weight': 0.05},
    'Recent Positive Credit Behavior': {'impact': 1, 'weight': 0.05},
    'Amounts Owed (High debt, high credit utilization)': {'impact': -1, 'weight': 0.10},
    'New Credit Accounts and Inquiries': {'impact': -1, 'weight': 0.05},
    'High Debt-to-Income Ratio (DTI)': {'impact': -1, 'weight': 0.05},
    'Bankruptcies, Liens, Foreclosures, or Collections': {'impact': -1, 'weight': 0.05},
    'Closing Old Credit Accounts': {'impact': -1, 'weight': 0.05},
    'Outstanding Loans or Defaulted Loans': {'impact': -1, 'weight': 0.05}
}

# Function to calculate FICO-like score
def calculate_credit_score(values):
    score = 300  # Minimum FICO score
    for factor, value in values.items():
        score += (factors[factor]['impact'] * value * factors[factor]['weight'] * 100)
    return max(min(score, 850), 300)

# Function for Default Risk Prediction
def predict_default_risk(input_data, model):
    prediction = model.predict_proba(input_data)[0, 1]  # Get probability of default
    return round(prediction * 100, 2)  # Convert to percentage risk

# Helper function for rendering SHAP plots
def st_shap(plot, height=None):
    """Helper function to display SHAP plots in Streamlit"""
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

# Streamlit UI
st.title('AI-Powered Credit Report Analysis')

# Sidebar for input
st.sidebar.header("Credit Factors")
factor_values = {factor: st.sidebar.slider(f"{factor} (0=Poor, 10=Excellent)", 0, 10, 7) for factor in factors.keys()}

# Calculate credit score
fico_score = calculate_credit_score(factor_values)

# Display the credit score
st.subheader("FICO-Like Credit Score")
st.write(f"Your credit score is: **{fico_score}**")

# Simulated dataset for Default Risk Prediction
rng = np.random.default_rng(42)  # Fix NumPy warning
X_train = rng.integers(0, 11, (500, len(factors)))
y_train = np.random.choice([0, 1], size=500, p=[0.8, 0.2])  # 80% non-default, 20% default

# Train a simple Random Forest model
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)

# Convert user input into a model-friendly format
user_input = np.array(list(factor_values.values()), dtype=float).reshape(1, -1)  # Ensure 2D input

# Predict default risk
default_risk = predict_default_risk(user_input, rf_model)
st.subheader("Default Risk Analysis")
st.write(f"Predicted risk of **defaulting on a loan**: **{default_risk}%**")

# Risk category
if default_risk < 20:
    st.success("🟢 Low Risk: Good Credit Standing")
elif 20 <= default_risk < 50:
    st.warning("🟡 Moderate Risk: Monitor Credit Behavior")
else:
    st.error("🔴 High Risk: Audit Recommended!")

# Fraud Detection using Isolation Forest
iso_forest = IsolationForest(contamination=0.05)  # 5% anomaly detection
iso_forest.fit(X_train)

fraud_score = iso_forest.decision_function(user_input)[0]  # Get anomaly score
fraud_risk = "🔴 High Fraud Risk" if fraud_score < -0.1 else "🟢 Low Fraud Risk"

st.subheader("Fraud Detection")
st.write(f"**Fraud Risk Assessment:** {fraud_risk}")

# SHAP Explainability
st.subheader("AI Explainability - SHAP Values")
explainer = shap.TreeExplainer(rf_model)

# Ensure SHAP values computation is valid
try:
    shap_values = explainer.shap_values(user_input)

    # Debug output
    st.write(f"SHAP values type: {type(shap_values)}")
    
    if isinstance(shap_values, list) and len(shap_values) > 0:
        shap_values = np.array(shap_values)
        if shap_values.ndim == 3:
            shap_values = shap_values[1]  # Select correct class if multi-class
        elif shap_values.ndim == 1:
            shap_values = shap_values.reshape(1, -1)  # Ensure 2D shape
    else:
        st.error("SHAP values computation failed.")
        shap_values = np.zeros((1, len(factors)))  # Default to zeros

    # Ensure correct shape for plotting
    feature_names = list(factors.keys())  # Convert dict_keys to list
    st.write(f"Feature names count: {len(feature_names)}")

    if shap_values.shape[1] == len(feature_names):
        st.subheader("SHAP Force Plot - AI Explainability")
        st_shap(shap.force_plot(explainer.expected_value, shap_values[0, :], user_input[0, :]))

        st.subheader("SHAP Summary Plot")
        fig, ax = plt.subplots()
        shap.summary_plot(shap_values, feature_names=feature_names, show=False)
        st.pyplot(fig)
    else:
        st.error(f"SHAP values shape mismatch: SHAP values {shap_values.shape}, features {len(feature_names)}")

except Exception as e:
    st.error(f"SHAP computation error: {e}")
