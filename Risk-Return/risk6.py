import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

# --- App Header ---
st.title("Interactive Finance Simulation: Risk and Return")
st.markdown("**Right Reserved with Dr. Joshi**")
st.sidebar.header("Simulation Controls")

# --- Time Duration and Frequency Change ---
st.sidebar.subheader("Select Time Duration and Frequency")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2023-01-01"))
frequency = st.sidebar.selectbox("Select Data Frequency", ["1d", "1wk", "1mo"])

# --- Data Fetching ---
st.sidebar.subheader("Select Tickers")
tickers = st.sidebar.text_input("Enter Stock Tickers (comma-separated)", "AAPL, MSFT, GOOGL, AMZN, TSLA")
tickers = tickers.split(",")

# Strip spaces from tickers
tickers = [ticker.strip() for ticker in tickers]

market_index = "^GSPC"  # S&P 500

if len(tickers) < 1:
    st.warning("Please select at least one stock.")
else:
    # Fetch Data
    data = yf.download(tickers + [market_index], start=start_date, end=end_date, interval=frequency)['Adj Close']
    returns = data.pct_change().dropna()

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

    # --- CAPM and Security Market Line for all tickers ---
    st.subheader("3. CAPM and Security Market Line")
    market_returns = returns[market_index]
    risk_free_rate = st.sidebar.slider("Risk-Free Rate", 0.01, 0.10, 0.03, key="risk_free_rate")
    market_premium = st.sidebar.slider("Market Risk Premium", 0.01, 0.10, 0.06)

    betas = []
    expected_returns_capm = []
    for stock in tickers:
        X = sm.add_constant(market_returns)
        Y = returns[stock]
        model = sm.OLS(Y, X).fit()
        beta = model.params[1]
        expected_return_capm = risk_free_rate + beta * market_premium
        betas.append(beta)
        expected_returns_capm.append(expected_return_capm)

    # Plot SML with all tickers' betas
    beta_range = np.linspace(0, 2, 100)
    sml = risk_free_rate + beta_range * market_premium
    plt.figure(figsize=(10, 5))
    plt.plot(beta_range, sml, label="SML")

    for i, stock in enumerate(tickers):
        plt.scatter(betas[i], expected_returns_capm[i],
                    label=f"{stock} (β={betas[i]:.2f}, E[Return]={expected_returns_capm[i]:.2%})")

    plt.title("Security Market Line (SML) for Selected Assets")
    plt.xlabel("Beta (β)")
    plt.ylabel("Expected Return")
    plt.legend()
    st.pyplot(plt)

    # --- Portfolio Risk and Return ---
    st.subheader("4. Portfolio Risk and Return")

    # Risk aversion slider
    risk_aversion = st.sidebar.slider("Risk Aversion Coefficient (A)", 0.5, 10.0, 3.0)

    # Select the weights for the assets in the portfolio
    num_assets = len(tickers)
    weights = []
    for i in range(num_assets):
        weight = st.sidebar.slider(f"Weight for {tickers[i]}", -1.0, 1.0, 1.0 / num_assets, step=0.01,
                                   key=f"weight_{tickers[i]}")
        weights.append(weight)

    # Normalize the weights so that they sum up to 1 (adjust for short-selling)
    weights = np.array(weights)
    if np.sum(weights) != 0:
        weights /= np.sum(weights)  # Normalize if the sum isn't zero

    # Calculate portfolio returns and covariance matrix
    portfolio_returns = returns[tickers].mean() * 252  # Annualize returns
    portfolio_cov_matrix = returns[tickers].cov() * 252  # Annualize covariance matrix

    # Check if the covariance matrix is valid
    if np.any(np.isnan(portfolio_cov_matrix)) or np.any(np.isinf(portfolio_cov_matrix)):
        st.warning("Covariance matrix contains invalid values.")
    else:
        # Portfolio Expected Return
        portfolio_expected_return = np.dot(weights, portfolio_returns)

        # Portfolio Volatility (Risk)
        try:
            portfolio_volatility = np.sqrt(np.dot(weights, np.dot(portfolio_cov_matrix, weights)))
        except ValueError:
            portfolio_volatility = np.nan  # If there's a matrix issue, set volatility to NaN

        # Calculate Portfolio Beta
        weighted_betas = np.dot(weights, betas)

        st.write(f"**Portfolio Expected Return:** {portfolio_expected_return:.2%}")
        st.write(f"**Portfolio Volatility (Risk):** {portfolio_volatility:.2%}")
        st.write(f"**Portfolio Beta:** {weighted_betas:.2f}")

    # --- Minimum and Maximum Portfolio Risk ---
    portfolio_risks = []

    for i in range(100):  # Simulating 100 random weight combinations
        random_weights = np.random.random(num_assets)
        random_weights /= random_weights.sum()

        portfolio_volatility = np.sqrt(np.dot(random_weights, np.dot(portfolio_cov_matrix, random_weights)))
        if not np.isnan(portfolio_volatility):
            portfolio_risks.append(portfolio_volatility)

    if portfolio_risks:
        min_risk = min(portfolio_risks)
        max_risk = max(portfolio_risks)
        st.write(f"**Minimum Portfolio Risk:** {min_risk:.2%}")
        st.write(f"**Maximum Portfolio Risk:** {max_risk:.2%}")
    else:
        st.write("**Minimum Portfolio Risk:** Invalid data")
        st.write("**Maximum Portfolio Risk:** Invalid data")

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

    # Calculate utility for the selected stock
    utility = portfolio_expected_return - 0.5 * risk_aversion * (portfolio_volatility ** 2)
    st.write(f"**Utility for Selected Portfolio (U):** {utility:.2f}")

    # Plot Utility Curve
    risk_levels = np.linspace(0.01, portfolio_volatility * 2, 100)
    utility_values = portfolio_expected_return - 0.5 * risk_aversion * (risk_levels ** 2)

    plt.figure(figsize=(10, 5))
    plt.plot(risk_levels, utility_values, label=f"Utility Curve (A={risk_aversion})")
    plt.axvline(x=portfolio_volatility, color='red', linestyle='--', label="Portfolio Risk")
    plt.axhline(y=utility, color='blue', linestyle='--', label="Portfolio Utility")
    plt.title("Utility Curve")
    plt.xlabel("Risk (Standard Deviation)")
    plt.ylabel("Utility")
    plt.legend()
    st.pyplot(plt)

    # --- Correlation of Assets ---
    st.subheader("7. Correlation of Assets and Portfolio Risk")
    correlation_matrix = returns[tickers].corr()
    st.write("**Correlation Matrix**")
    st.write(correlation_matrix)

    # Impact of Correlation on Portfolio Risk
    st.subheader("Impact of Correlation on Portfolio Risk")

    correlations = np.linspace(-1, 1, 21)
    portfolio_volatilities = []

    for corr in correlations:
        modified_cov_matrix = correlation_matrix * corr
        portfolio_volatility = np.sqrt(np.dot(weights, np.dot(modified_cov_matrix, weights)))
        portfolio_volatilities.append(portfolio_volatility)

    plt.figure(figsize=(10, 5))
    plt.plot(correlations, portfolio_volatilities, label="Portfolio Volatility")
    plt.title("Portfolio Volatility vs. Asset Correlation")
    plt.xlabel("Correlation Coefficient")
    plt.ylabel("Portfolio Volatility")
    st.pyplot(plt)
