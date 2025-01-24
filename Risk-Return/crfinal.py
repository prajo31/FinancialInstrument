import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Define credit score factors (both boosting and damaging)
factors = {
    # Credit-Boosting Factors
    'Payment History': {'impact': 1, 'weight': 0.15},  # Positive impact
    'Credit Mix': {'impact': 1, 'weight': 0.10},  # Positive impact
    'Length of Credit History': {'impact': 1, 'weight': 0.10},  # Positive impact
    'Credit Utilization (keep below 30%)': {'impact': 1, 'weight': 0.10},  # Positive impact (lower is better)
    'Total Accounts in Good Standing': {'impact': 1, 'weight': 0.10},  # Positive impact
    'Loan Payment History': {'impact': 1, 'weight': 0.05},  # Positive impact
    'Recent Positive Credit Behavior': {'impact': 1, 'weight': 0.05},  # Positive impact

    # Credit-Damaging Factors
    'Amounts Owed (High debt, high credit utilization)': {'impact': -1, 'weight': 0.10},  # Negative impact
    'New Credit Accounts and Inquiries': {'impact': -1, 'weight': 0.05},  # Negative impact
    'High Debt-to-Income Ratio (DTI)': {'impact': -1, 'weight': 0.05},  # Negative impact
    'Bankruptcies, Liens, Foreclosures, or Collections': {'impact': -1, 'weight': 0.05},  # Negative impact
    'Closing Old Credit Accounts': {'impact': -1, 'weight': 0.05},  # Negative impact
    'Outstanding Loans or Defaulted Loans': {'impact': -1, 'weight': 0.05}  # Negative impact
}


# Function to calculate FICO-like score
def calculate_credit_score(values):
    score = 300  # Minimum FICO score
    for factor, value in values.items():
        score += (factors[factor]['impact'] * value * factors[factor]['weight'] * 100)
    score = max(min(score, 850), 300)  # Ensure score is between 300 and 850
    return score


# Function to give personalized recommendations based on user input
def personalized_recommendations(values, current_score):
    recommendations = []
    for factor, value in values.items():
        if factors[factor]['impact'] == 1 and value < 7:  # Positive factors that could be improved
            recommendations.append(f"Improve {factor} (current score: {value}) to boost your score.")
        elif factors[factor]['impact'] == -1 and value > 7:  # Negative factors that could be worsened
            recommendations.append(f"Decrease {factor} (current score: {value}) to improve your score.")

    if current_score < 600:
        recommendations.append(
            "Consider focusing on increasing positive factors like Payment History and Credit Utilization.")

    return recommendations


# Streamlit app layout
st.title('Credit Score Calculation App')

# Sliders for user input
st.sidebar.header("Credit Factors")

payment_history = st.sidebar.slider("Payment History (0=Poor, 10=Excellent)", 0, 10, 8)
credit_mix = st.sidebar.slider("Credit Mix (0=Poor, 10=Excellent)", 0, 10, 7)
length_of_credit_history = st.sidebar.slider("Length of Credit History (0=Short, 10=Long)", 0, 10, 7)
credit_utilization = st.sidebar.slider("Credit Utilization (keep below 30%)", 0, 10, 3)
total_accounts_good_standing = st.sidebar.slider("Total Accounts in Good Standing (0=Few, 10=Many)", 0, 10, 8)
loan_payment_history = st.sidebar.slider("Loan Payment History (0=Poor, 10=Excellent)", 0, 10, 7)
recent_positive_credit_behavior = st.sidebar.slider("Recent Positive Credit Behavior (0=None, 10=Many)", 0, 10, 6)

amounts_owed = st.sidebar.slider("Amounts Owed (0=Low, 10=High)", 0, 10, 2)
new_credit_accounts_inquiries = st.sidebar.slider("New Credit Accounts and Inquiries (0=None, 10=Many)", 0, 10, 3)
high_dti = st.sidebar.slider("High Debt-to-Income Ratio (DTI) (0=Low, 10=High)", 0, 10, 4)
bankruptcies_liens = st.sidebar.slider("Bankruptcies, Liens, Foreclosures, or Collections (0=None, 10=Many)", 0, 10, 1)
closing_old_accounts = st.sidebar.slider("Closing Old Credit Accounts (0=None, 10=Many)", 0, 10, 2)
outstanding_defaulted_loans = st.sidebar.slider("Outstanding Loans or Defaulted Loans (0=None, 10=Many)", 0, 10, 1)

# Dictionary to store the values for calculation
factor_values = {
    'Payment History': payment_history,
    'Credit Mix': credit_mix,
    'Length of Credit History': length_of_credit_history,
    'Credit Utilization (keep below 30%)': credit_utilization,
    'Total Accounts in Good Standing': total_accounts_good_standing,
    'Loan Payment History': loan_payment_history,
    'Recent Positive Credit Behavior': recent_positive_credit_behavior,
    'Amounts Owed (High debt, high credit utilization)': amounts_owed,
    'New Credit Accounts and Inquiries': new_credit_accounts_inquiries,
    'High Debt-to-Income Ratio (DTI)': high_dti,
    'Bankruptcies, Liens, Foreclosures, or Collections': bankruptcies_liens,
    'Closing Old Credit Accounts': closing_old_accounts,
    'Outstanding Loans or Defaulted Loans': outstanding_defaulted_loans
}

# Calculate the credit score
fico_score = calculate_credit_score(factor_values)

# Display the results
st.subheader("FICO-Like Credit Score")
st.write(f"Your credit score is: {fico_score}")

# Display personalized recommendations
recommendations = personalized_recommendations(factor_values, fico_score)
st.write("### Recommendations to Improve Your Credit Score:")
for rec in recommendations:
    st.write(f"- {rec}")

# Display a bar chart of the factors
fig, ax = plt.subplots()
factor_names = list(factors.keys())
# Compute impact with correct sign adjustments
factor_impact = []
for factor in factor_names:
    value = factor_values[factor]
    impact = factors[factor]['impact']
    weight = factors[factor]['weight']

    # Adjust the sign of the impact for negative factors (lower values improve the score)
    if impact == -1:
        contribution = -impact * (10 - value) * weight * 100
    else:
        contribution = impact * value * weight * 100

    factor_impact.append(contribution)

# Dynamically calculate colors and ensure positive/negative scale
bar_colors = [
    'green' if impact > 0 else 'red'
    for impact in factor_impact
]

# Create the horizontal bar chart
ax.barh(factor_names, factor_impact, color=bar_colors)

# Add a vertical line at 0 for visual clarity
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')

# Adding labels and title to the bar chart
ax.set_xlabel('Impact on Credit Score')
ax.set_ylabel('Credit Factors')
ax.set_title('Impact of Each Factor on Credit Score')

# Update the plot in Streamlit
st.pyplot(fig)


# Button to display more details
if st.button("Show Factors Contributing to Credit Score"):
    st.write("### Factors Contributing to Credit Score:")
    for factor, details in factors.items():
        impact = "Improves" if details['impact'] == 1 else "Decreases"
        st.write(f"{factor}: {impact} (Weight: {details['weight'] * 100}%)")
