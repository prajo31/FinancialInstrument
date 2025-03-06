import yfinance as yf
import pandas as pd


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
    print(f"Total Dividend in Last Year (D0): ${D0:.2f}")
    print(f"Next Period Dividend (D1): ${D1:.2f}")
    print(f"Annual Growth Rate: {annualized_growth:.2%}")
    print(f"Dividend Yield: {dividend_yield:.2%}")
    print(f"Required Return (R): {required_return:.2%}")

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
        "Estimated Stock Price": stock_price
    }


# Example usage
ticker = "AAPL"  # Replace with the desired stock ticker
result = annual_dividend_growth_from_history(ticker)

if isinstance(result, str):
    print(result)
else:
    print("Annual Growth Rates:")
    for year, growth in result["Annual Growth Rates"].items():
        print(f"{year}: {growth:.2%}")
    print(f"\nAverage Annual Growth Rate: {result['Average Annual Growth Rate']:.2%}")
    print(f"Annualized Growth Rate: {result['Annualized Growth Rate']:.2%}")
    print(f"Dividend Yield: {result['Dividend Yield']:.2%}")
    print(f"Required Return: {result['Required Return']:.2%}")
    print(f"Estimated Stock Price: ${result['Estimated Stock Price']:.2f}")
