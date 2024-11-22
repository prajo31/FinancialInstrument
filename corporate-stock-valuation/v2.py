import yfinance as yf
import pandas as pd
import streamlit as st


def annual_dividend_growth_from_history(ticker, period="5y"):
    """
    Calculate the annual dividend growth rate using historical data from yfinance,
    then estimate the stock price using the Dividend Discount Model (DDM).

    Parameters:
        ticker (str): Stock ticker symbol.
        period (str): Period for fetching historical data (e.g., '5y').

    Returns:
        dict: Annual growth rates, average growth rate, dividend yield,
              required return, and estimated stock price (P0).
    """
    # Fetch historical data with actions (including dividends)
    stock = yf.Ticker(ticker)
    historical_data = stock.history(period=period, actions=True)

    # Fetch the actual stock price (latest closing price)
    actual_price = stock.history(period="1d")['Close'].iloc[0]

    # Extract dividends
    if 'Dividends' not in historical_data.columns or historical_data['Dividends'].sum() == 0:
        return f"No dividend data available for {ticker} in the given period."

    dividend_data = historical_data[['Dividends']].dropna()

    # Group by year
    dividend_data['Year'] = dividend_data.index.year
    annual_dividends = dividend_data.groupby('Year').sum()

    # Calculate yearly growth rates
    annual_dividends['Growth Rate'] = annual_dividends['Dividends'].pct_change()

    # Remove inf or NaN values caused by dividing by zero or missing data
    valid_growth_rates = annual_dividends['Growth Rate'].replace([float('inf'), -float('inf')], float('nan')).dropna()

    # Average yearly growth rate
    average_growth = valid_growth_rates.mean()

    # Annualize the growth rate (same as annual growth for yearly data)
    annualized_growth = average_growth

    # Fetch dividend yield from stock.info
    dividend_yield = stock.info.get('dividendYield', 0)

    # Calculate required return
    required_return = dividend_yield + annualized_growth

    # Get the total dividend for the last year (D0)
    last_year_dividend = annual_dividends.tail(1)['Dividends'].iloc[0]  # Total dividend for the last year
    D0 = last_year_dividend  # This is the dividend paid in the last full year

    # Calculate D1 (next period dividend)
    D1 = D0 * (1 + annualized_growth)

    # Debugging: Print intermediate values
    st.write(f"Total Dividend in Last Year (D0): ${D0:.2f}")
    st.write(f"Next Period Dividend (D1): ${D1:.2f}")
    st.write(f"Annual Growth Rate: {annualized_growth:.2%}")
    st.write(f"Dividend Yield: {dividend_yield:.2%}")
    st.write(f"Required Return (R): {required_return:.2%}")
    st.write(f"**Actual Stock Price**: ${actual_price:.2f}")  # Display actual stock price

    # Calculate stock price using the Dividend Discount Model (DDM)

    # Calculate stock price using the Dividend Discount Model (DDM)
    if required_return > annualized_growth:  # Ensure R > g
        stock_price = D1 / (required_return - annualized_growth)
    else:
        stock_price = None  # If R <= g, the formula doesn't work (price would be infinite)

    # Return results
    return {
        "Annual Growth Rates": valid_growth_rates.to_dict(),
        "Average Annual Growth Rate": average_growth,
        "Annualized Growth Rate": annualized_growth,
        "Dividend Yield": dividend_yield,
        "Required Return": required_return,
        "Estimated Stock Price": stock_price,
        "Actual Stock Price": actual_price
    }


# Streamlit App Interface
st.title("Dividend Discount Model (DDM) Stock Price Estimator")

ticker_input = st.text_input("Enter Stock Ticker", "AAPL")  # Default to "AAPL"

if ticker_input:
    result = annual_dividend_growth_from_history(ticker_input)

    if isinstance(result, str):
        st.error(result)  # Display error if no data available
    else:
        st.subheader("Annual Growth Rates:")
        for year, growth in result["Annual Growth Rates"].items():
            st.write(f"{year}: {growth:.2%}")

        st.write(f"\n**Average Annual Growth Rate**: {result['Average Annual Growth Rate']:.2%}")
        st.write(f"**Annualized Growth Rate**: {result['Annualized Growth Rate']:.2%}")
        st.write(f"**Dividend Yield**: {result['Dividend Yield']:.2%}")
        st.write(f"**Required Return (R)**: {result['Required Return']:.2%}")

        if result["Estimated Stock Price"] is not None:
            st.write(f"**Estimated Stock Price**: ${result['Estimated Stock Price']:.2f}")
        else:
            st.warning("Stock price calculation is not possible due to invalid required return (R <= g).")

            # Display the actual stock price
            st.write(f"**Actual Stock Price**: ${result['Actual Stock Price']:.2f}")
