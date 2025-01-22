import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# --- App Header ---
st.title("Interactive Finance Simulation: Risk and Return")
st.sidebar.header("Simulation Controls")

# --- Data Fetching ---
st.sidebar.subheader("Select Tickers")
tickers = st.sidebar.multiselect("Choose Stocks", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"], default=["AAPL", "MSFT"])
market_index = "^GSPC"  # S&P 500

if len(tickers) < 1:
    st.warning("Please select at least one stock.")
else:
    # Fetch Data
    ddata = yf.download(tickers + [market_index], start=start_date, end=end_date) ['Adj Close']
    # Access 'Adj Close' for all tickers and the market index
    returns = adj_close_data.pct_change().dropna()

    st.subheader("Sample Data")
    st.write(data.tail())

    # --- Probability Distribution ---
    st.subheader("1. Probability Distribution")
    stock = st.selectbox("Select a Stock", tickers)
    plt.figure(figsize=(10, 5))
    plt.hist(returns[stock], bins=50, density=True, alpha=0.7, color='blue')
    plt.title(f"Probability Distribution of {stock} Returns")
    plt.xlabel("Daily Returns")
    plt.ylabel("Frequency")
    st.pyplot(plt)

    # --- Expected Return and Standard Deviation ---
    st.subheader("2. Expected Return and Standard Deviation")
    expected_return = returns[stock].mean() * 252
    std_dev = returns[stock].std() * (252 ** 0.5)
    st.write(f"**Expected Return (Annualized):** {expected_return:.2%}")
    st.write(f"**Standard Deviation (Annualized):** {std_dev:.2%}")

    # --- CAPM and Security Market Line ---
    st.subheader("3. CAPM and Security Market Line")
    market_returns = returns[market_index]
    X = sm.add_constant(market_returns)
    Y = returns[stock]
    model = sm.OLS(Y, X).fit()
    beta = model.params[1]
    risk_free_rate = st.sidebar.slider("Risk-Free Rate", 0.01, 0.10, 0.03)
    market_premium = st.sidebar.slider("Market Risk Premium", 0.01, 0.10, 0.06)
    expected_return_capm = risk_free_rate + beta * market_premium

    st.write(f"**Beta (β):** {beta:.2f}")
    st.write(f"**Expected Return (CAPM):** {expected_return_capm:.2%}")

    beta_range = np.linspace(0, 2, 100)
    sml = risk_free_rate + beta_range * market_premium
    plt.figure(figsize=(10, 5))
    plt.plot(beta_range, sml, label="SML")
    plt.scatter(beta, expected_return_capm, color='red', label=stock)
    plt.title("Security Market Line (SML)")
    plt.xlabel("Beta (β)")
    plt.ylabel("Expected Return")
    plt.legend()
    st.pyplot(plt)

    # --- Portfolio Risk and Return ---
    st.subheader("4. Portfolio Risk and Return")
    weights = st.sidebar.slider("Weight for Portfolio", 0.0, 1.0, 0.5)
    portfolio_returns = returns[tickers].mean() * 252
    portfolio_cov_matrix = returns[tickers].cov() * 252
    portfolio_expected_return = np.dot([weights, 1 - weights], portfolio_returns)
    portfolio_volatility = np.sqrt(np.dot([weights, 1 - weights], np.dot(portfolio_cov_matrix, [weights, 1 - weights])))

    st.write(f"**Portfolio Expected Return:** {portfolio_expected_return:.2%}")
    st.write(f"**Portfolio Volatility (Risk):** {portfolio_volatility:.2%}")

    # --- Diversification ---
    st.subheader("5. Diversification: Systematic vs Diversifiable Risk")
    num_stocks = np.arange(1, 51)
    diversifiable_risk = 1 / np.sqrt(num_stocks)
    plt.figure(figsize=(10, 5))
    plt.plot(num_stocks, diversifiable_risk, label="Diversifiable Risk")
    plt.axhline(y=0.2, color='red', linestyle='--', label="Market Risk")
    plt.title("Diversifiable vs. Market Risk")
    plt.xlabel("Number of Stocks in Portfolio")
    plt.ylabel("Risk")
    plt.legend()
    st.pyplot(plt)

    # --- Risk Aversion and Utility Curves ---
    st.subheader("6. Risk Aversion and Utility Curves")

    # Risk aversion slider
    risk_aversion = st.sidebar.slider("Risk Aversion Coefficient (A)", 0.5, 10.0, 3.0)

    # Calculate utility for the selected stock
    utility = expected_return - 0.5 * risk_aversion * (std_dev ** 2)
    st.write(f"**Utility for Selected Stock (U):** {utility:.2f}")

    # Plot Utility Curve
    risk_levels = np.linspace(0.01, std_dev * 2, 100)
    utility_values = expected_return - 0.5 * risk_aversion * (risk_levels ** 2)

    plt.figure(figsize=(10, 5))
    plt.plot(risk_levels, utility_values, label=f"Utility Curve (A={risk_aversion})")
    plt.axvline(x=std_dev, color='red', linestyle='--', label="Stock Risk")
    plt.axhline(y=utility, color='blue', linestyle='--', label="Stock Utility")
    plt.title("Utility Curve")
    plt.xlabel("Risk (Standard Deviation)")
    plt.ylabel("Utility")
    plt.legend()
    st.pyplot(plt)
