import yfinance as yf
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
from fredapi import Fred


@dataclass
class StockValuation:
    ticker: str
    discount_rate: float = field(init=False)

    def fetch_dividend(self) -> pd.Series:
        """Fetch historical dividend data using yfinance."""
        stock = yf.Ticker(self.ticker)
        dividends = stock.dividends
        if dividends.empty:
            raise ValueError("No dividends found.")
        return dividends


@dataclass
class DDMValuation(StockValuation):
    api_key: str
    fred: Fred = field(init=False)  # Fred client instance
    risk_free_rate: float = field(init=False)
    market_return: float = field(init=False)
    growth_rate: float = field(init=False, default=None)
    dividend: float = field(init=False, default=None)

    def __post_init__(self):
        """Fetch risk-free rate and market return, and calculate discount rate."""
        self.fred = Fred(api_key=self.api_key)
        self.risk_free_rate = self.fetch_risk_free_rate()
        self.market_return = self.calculate_market_return("^GSPC")
        self.discount_rate = self.calculate_discount_rate()

    def fetch_risk_free_rate(self) -> float:
        """Fetch the 10-year Treasury yield from Fred."""
        data = self.fred.get_series('DGS10').dropna()
        latest_value = data.iloc[-1] / 100  # Get the latest non-NaN value
        return float(latest_value)

    def calculate_market_return(self, index_ticker: str) -> float:
        """Calculate the geometric market return using S&P 500 data."""
        data = yf.Ticker(index_ticker).history(period='5y')['Close']
        if data.empty:
            raise ValueError(f"No data found for {index_ticker}.")

        daily_return = data.pct_change().dropna() # Calculate daily returns
        average_daily_returns = daily_return.mean()
        eagr_daily = ( 1 + average_daily_returns) ** 252 - 1
        print(f"Calculated Annual Growth Rate (Daily): {eagr_daily:.2%}")
        return eagr_daily

    def calculate_discount_rate(self) -> float:
        """Calculate the discount rate using CAPM."""
        stock = yf.Ticker(self.ticker)
        beta = stock.info.get("beta")
        if beta is None:
            raise ValueError("No beta found.")

        discount_rate = self.risk_free_rate + beta * (self.market_return - self.risk_free_rate)
        print(f"Calculated discount rate: {discount_rate:.2%}")
        return discount_rate

    def calculate_dividends_eagr(self) -> float:
        """Calculate the Compound Annual Growth Rate (CAGR) of dividends."""
        dividends = self.fetch_dividend()
        if len(dividends) < 4: # Ensure there are enough quarters
            raise ValueError(f"Not enough dividend data to calculate quarterly growth rate.")

        # Calculate the growth rate from the latest dividend to the earliest in the last year
        start_dividend = dividends.iloc[-4]  # Dividend from four quarters ago
        end_dividend = dividends.iloc[-1]  # Most recent dividend
        quarterly_growth_rate = (end_dividend / start_dividend) - 1

        # Convert quarterly growth rate to EAGR
        eagr_quarterly = (1 + quarterly_growth_rate) ** 4 - 1  # 4 quarters in a year
        print(f"Effective Annual Growth Rate (Quarterly): {eagr_quarterly:.2%}")

        # Assign calculated growth rate to the class attribut
        self.growth_rate = eagr_quarterly
        return eagr_quarterly

    def calculate_value(self) -> float:
        """Calculate the intrinsic value of the stock using DDM."""
        if self.dividend is None or self.growth_rate is None:
            raise ValueError("Data not fetched. Please call fetch_data().")
        if self.discount_rate <= self.growth_rate:
            raise ValueError("Discount rate must be greater than growth rate.")

        intrinsic_value = self.dividend / (self.discount_rate - self.growth_rate)
        return intrinsic_value

    def run_valuation(self):
        """Fetch data, calculate growth, and print the intrinsic value."""
        self.dividend = self.fetch_dividend().iloc[-1]  # Get latest dividend
        self.calculate_dividends_eagr()  # Calculate EAGR for dividends


        intrinsic_value = self.calculate_value()  # Calculate intrinsic value

        # Print all relevant information
        print(f"\nStock Ticker: {self.ticker}")
        print(f"Latest Dividend: ${self.dividend:.2f}")
        print(f"Risk-Free Rate: {self.risk_free_rate:.2%}")
        print(f"Market Return: {self.market_return:.2%}")
        print(f"Discount Rate: {self.discount_rate:.2%}")
        print(f"Effective Annual Growth Rate (EAGR): {self.growth_rate:.2%}")
        print(f"Intrinsic Value: ${intrinsic_value:.2f}")


# Usage Example
if __name__ == "__main__":
    # Initialize the DDMValuation class with AAPL stock and run valuation in one line
    valuation = DDMValuation(ticker='MSFT', api_key="dfd58fd99d4b4dd58a835307f6b8c89d")
    valuation.run_valuation()
