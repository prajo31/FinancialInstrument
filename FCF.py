# --- Created and Maintained by Dr. Joshi ---
# --- All Rights Reserved ---

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

# --- File to store leaderboard ---
LEADERBOARD_FILE = "leaderboard5.csv"

# --- Function to fetch live stock data ---
@st.cache_data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    cashflow = stock.cashflow
    financials = stock.financials
    history = stock.history(period="1d")
    return financials, cashflow, history['Close'].iloc[-1]

# --- Function to calculate FCF ---
def calculate_fcf(financials, cashflow):
    ebit = financials.loc['EBIT'].iloc[0]
    capex = -cashflow.loc['Capital Expenditure'].iloc[0]
    depreciation = cashflow.loc['Depreciation And Amortization'].iloc[0]
    nwc_change = cashflow.loc['Change In Working Capital'].iloc[0]
    tax_rate = 0.21  # Fixed for simplicity
    fcf = (ebit * (1 - tax_rate) + depreciation - capex - nwc_change) / 1_000_000_000
    return fcf

# --- Function to save leaderboard to CSV ---
def save_leaderboard(leaderboard):
    leaderboard.to_csv(LEADERBOARD_FILE, index=False)

# --- Function to load leaderboard from CSV ---
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        return pd.read_csv(LEADERBOARD_FILE)
    return pd.DataFrame(columns=['Name', 'Prediction', 'Market Price', 'Error', 'Status'])

# --- Main Application Interface ---
st.title("Free Cash Flow Estimation with Intrinsic Value")

# --- User Inputs ---
while True:
    ticker = st.text_input("Enter stock ticker (visit finance.yahoo.com to find Ticker Symbol):", "AAPL")
    try:
        if ticker:
            financials, cashflow, current_price = get_stock_data(ticker)
            break
    except Exception as e:
        st.warning(
            f"Could not find data for symbol '{ticker}'. Please check your input or visit finance.yahoo.com.")  # Warn if there is an error

fcf = calculate_fcf(financials, cashflow)
st.write(f"Current Free Cash Flow (in Billion): ${fcf:,.2f}")

# --- Growth Rate and Discount Rate Inputs without Limits ---
growth_rate = st.number_input("Enter growth rate of FCF (%):", value=3.0) / 100
discount_rate = st.number_input("Enter discount rate (WACC) (%):", value=8.0) / 100
years = st.slider("Forecast period (years)", 1, 10, 5)

# --- Forecast FCF ---
fcf_forecast = [fcf * (1 + growth_rate) ** t for t in range(1, years + 1)]
terminal_value = fcf_forecast[-1] / (discount_rate - growth_rate)
intrinsic_value = sum([fcf_t / (1 + discount_rate) ** t for t, fcf_t in enumerate(fcf_forecast, start=1)]) + (terminal_value / (1 + discount_rate) ** years)
st.write(f"Intrinsic Value per Share: ${intrinsic_value:,.2f}")

# --- Compare with Market Price ---
st.write(f"Current Stock Price: ${current_price:.2f}")
if intrinsic_value > current_price:
    st.success("The stock is undervalued!")
else:
    st.warning("The stock is overvalued!")

# --- Sensitivity Analysis ---
st.subheader("Sensitivity Analysis")
growth_values = np.linspace(0.01, 0.10, 10)
discount_values = np.linspace(0.05, 0.15, 10)

sensitivity = pd.DataFrame(
    [[sum([fcf * (1 + g) ** t / (1 + r) ** t for t in range(1, years + 1)] +
          [fcf * (1 + g) ** years / (r - g) / (1 + r) ** years])
      for r in discount_values] for g in growth_values],
    columns=[f"{r:.2%}" for r in discount_values],
    index=[f"{g:.2%}" for g in growth_values]
)

st.dataframe(sensitivity)

# --- Plotly Chart: Forecasted FCF ---
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(range(1, years + 1)),
    y=fcf_forecast,
    mode='lines+markers',
    name='Forecasted FCF'
))
fig.update_layout(title='Forecasted Free Cash Flow Over Time',
                  xaxis_title='Year',
                  yaxis_title='FCF (in USD)')
st.plotly_chart(fig)

# --- Leaderboard: Store and Display Student Predictions ---
st.subheader("Leaderboard: Student Predictions")

# Initialize or Load Leaderboard
if 'leaderboard' not in st.session_state:
    st.session_state['leaderboard'] = load_leaderboard()

# Refresh Leaderboard Button
if st.button("Refresh Leaderboard"):
    st.session_state['leaderboard'] = pd.DataFrame(columns=['Name', 'Prediction', 'Market Price', 'Error', 'Status'])
    save_leaderboard(st.session_state['leaderboard'])  # Save empty leaderboard to CSV
    st.success("Leaderboard has been refreshed!")

# Input for Student Prediction
with st.form("prediction_form"):
    name = st.text_input("Enter your name:").strip().lower()  # Normalize name to lowercase
    prediction = st.number_input("Your predicted intrinsic value:", value=float(intrinsic_value))
    submit = st.form_submit_button("Submit Prediction")

# Store Prediction in Leaderboard
if submit:
    if name in st.session_state['leaderboard']['Name'].str.lower().values:
        st.warning("You have already submitted a prediction!")
    else:
        error = abs(prediction - current_price)
        status = "Undervalued" if prediction > current_price else "Overvalued"
        new_entry = pd.DataFrame([[name, prediction, current_price, error, status]],
                                 columns=['Name', 'Prediction', 'Market Price', 'Error', 'Status'])
        st.session_state['leaderboard'] = pd.concat([st.session_state['leaderboard'], new_entry], ignore_index=True)
        save_leaderboard(st.session_state['leaderboard'])  # Save updated leaderboard to CSV
        st.success("Prediction submitted successfully!")

# Display Leaderboard
leaderboard = st.session_state['leaderboard'].sort_values(by='Error', ascending=True)
st.write(leaderboard)

# --- Download Option ---
csv = leaderboard.to_csv(index=False).encode('utf-8')
st.download_button("Download Leaderboard", csv, "leaderboard.csv", "text/csv")
