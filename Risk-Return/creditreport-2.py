#Looks good except the contributing factors op top still green in negative zone and
# some factors not imrovimg credit scores turn green
import streamlit as st
import matplotlib.pyplot as plt

# Define credit score factors with proper weighting and impact
factors = {
    # Credit-Boosting Factors
    'Payment History': {'impact': 1, 'weight': 0.2},  # Positive impact
    'Credit Mix': {'impact': 1, 'weight': 0.15},  # Positive impact
    'Length of Credit History': {'impact': 1, 'weight': 0.1},  # Positive impact
    'Credit Utilization (keep below 30%)': {'impact': 1, 'weight': 0.1},  # Positive impact (lower is better)
    'Total Accounts in Good Standing': {'impact': 1, 'weight': 0.1},  # Positive impact
    'Loan Payment History': {'impact': 1, 'weight': 0.05},  # Positive impact
    'Recent Positive Credit Behavior': {'impact': 1, 'weight': 0.05},  # Positive impact

    # Credit-Damaging Factors
    'Amounts Owed (High debt, high credit utilization)': {'impact': -1, 'weight': 0.1},  # Negative impact (more owed = worse)
    'New Credit Accounts and Inquiries': {'impact': -1, 'weight': 0.05},  # Negative impact (too many inquiries = worse)
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

# Streamlit app layout
st.title('Credit Score Calculation App')

# Sliders for user input
st.sidebar.header("Credit Factors")

# Slider for each factor
payment_history = st.sidebar.slider("Payment History (0=Poor, 10=Excellent)", 0, 10, 8)
credit_mix = st.sidebar.slider("Credit Mix (0=Poor, 10=Excellent)", 0, 10, 7)
length_of_credit_history = st.sidebar.slider("Length of Credit History (0=Short, 10=Long)", 0, 10, 7)
credit_utilization = st.sidebar.slider("Credit Utilization (keep below 30%)", 0, 10, 3)
total_accounts_good_standing = st.sidebar.slider("Total Accounts in Good Standing (0=Few, 10=Many)", 0, 10, 8)
loan_payment_history = st.sidebar.slider("Loan Payment History (0=Poor, 10=Excellent)", 0, 10, 7)
recent_positive_credit_behavior = st.sidebar.slider("Recent Positive Credit Behavior (0=None, 10=Many)", 0, 10, 6)

# Damaging factors sliders
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

# Create a color-coded flag for each factor based on the slider value
def flag_color(value, factor):
    # Positive factors should be green when high, negative factors red when high
    if factors[factor]['impact'] == 1:  # Positive impact
        if value >= 8:
            return 'green'
        elif value >= 5:
            return 'yellow'
        else:
            return 'red'
    else:  # Negative impact
        if value >= 8:
            return 'red'
        elif value >= 5:
            return 'yellow'
        else:
            return 'green'

# Display factor impact and flags
for factor, value in factor_values.items():
    flag = flag_color(value, factor)
    st.write(f"{factor}: {flag} ({value})")

# Optionally display a bar chart of the factors
fig, ax = plt.subplots()
factor_names = list(factors.keys())
factor_values_list = [factor_values[factor] for factor in factor_names]
factor_impact = [factors[factor]['impact'] * factor_values[factor] * factors[factor]['weight'] * 100 for factor in factor_names]
ax.barh(factor_names, factor_impact, color=[flag_color(factor_values[factor], factor) for factor in factor_names])

# Adding labels and title to the bar chart
ax.set_xlabel('Impact on Credit Score')
ax.set_ylabel('Credit Factors')
ax.set_title('Impact of Each Factor on Credit Score')

st.pyplot(fig)
