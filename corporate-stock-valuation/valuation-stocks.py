import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Fetching company data from Yahoo Finance
def fetch_data(ticker):
    # Fetch data using yfinance API
    stock = yf.Ticker(ticker)
    info = stock.info
    cashflow = stock.cashflow
    financials = stock.financials

    # Extract required data
    market_price = info['currentPrice']
    dividends = info['dividendYield'] if 'dividendYield' in info else 0
    last_annual_dividend = info['dividendRate'] if 'dividendRate' in info else 0
    total_debt = info['totalDebt'] if 'totalDebt' in info else 0
    cash = info['totalCash'] if 'cash' in info else 0

    # Other relevant information
    operating_income = financials.loc['EBIT'].iloc[0]
    capex = -cashflow.loc['Capital Expenditure'].iloc[0]
    depreciation = cashflow.loc['Depreciation And Amortization'].iloc[0]
    working_capital_change = cashflow.loc['Change In Working Capital'].iloc[0]

    return {
        'market_price': market_price,
        'dividends': dividends,
        'last_annual_dividend': last_annual_dividend,
        'total_debt': total_debt,
        'cash': cash,
        'operating_income': operating_income,
        'capex': capex,
        'depreciation': depreciation,
        'working_capital_change': working_capital_change,
    }


# Free Cash Flow (FCF) Calculation
def calculate_fcf(operating_income, capex, depreciation, working_capital_change):
    return (operating_income * (1 - tax_rate) - capex - working_capital_change + depreciation) / 1000000000


# Valuation Model: Constant Growth (Gordon Growth Model)
def constant_growth_model(fcf_last, growth_rate, wacc):
    terminal_value = (fcf_last * (1 + growth_rate)) / (wacc - growth_rate)
    return terminal_value


# Discount Future Cash Flows to Present Value
def discount_fcf(fcf, wacc, years):
    return fcf / (1 + wacc) ** years


# Multi-stage Growth Model (for simplicity, we will use two stages)
def multi_stage_growth_model(fcf, growth_rate_initial, growth_rate_terminal, wacc, years_initial, years_terminal):
    fcf_initial = fcf
    fcf_future = []

    # First stage with high growth rate
    for year in range(1, years_initial + 1):
        fcf_future.append(discount_fcf(fcf_initial * (1 + growth_rate_initial) ** year, wacc, year))

    # Second stage with terminal growth rate
    fcf_terminal = fcf_initial * (1 + growth_rate_initial) ** years_initial * (1 + growth_rate_terminal)
    terminal_value = constant_growth_model(fcf_terminal, growth_rate_terminal, wacc)
    fcf_future.append(terminal_value / (1 + wacc) ** years_initial)

    return sum(fcf_future)


# Estimate the company's value
def estimate_company_value(ticker, growth_rate, wacc, years):
    data = fetch_data(ticker)
    fcf = calculate_fcf(data['operating_income'], data['capex'], data['depreciation'], data['working_capital_change'])

    # Using Multi-stage Growth Model for valuation
    company_value = multi_stage_growth_model(fcf, growth_rate, growth_rate, wacc, years, 0)

    # Include nonoperating assets (cash)
    company_value += data['cash']

    # Estimate the price-to-value ratio (P0)
    price_to_value = company_value / data['market_price']

    return company_value, price_to_value, data['market_price']


# Capital Gains Yield
def capital_gains_yield(current_price, estimated_price):
    return (estimated_price - current_price) / current_price


# Dividend Yield
def dividend_yield(dividend_per_share, current_price):
    return dividend_per_share / current_price


# Expected Total Return
def expected_total_return(capital_gains, dividend_yield):
    return capital_gains + dividend_yield


# Plotting Results
def plot_results(growth_rates, company_values, market_prices):
    plt.plot(growth_rates, company_values, label='Estimated Company Value')
    plt.plot(growth_rates, market_prices, label='Market Price', linestyle='--')
    plt.xlabel('Growth Rate')
    plt.ylabel('Company Value ($)')
    plt.title('Company Valuation vs Market Price')
    plt.legend()
    plt.grid(True)
    plt.show()


# Main Simulation Function
def run_simulation(ticker, growth_rate_range, wacc, years):
    company_values = []
    market_prices = []

    for growth_rate in growth_rate_range:
        company_value, price_to_value, market_price = estimate_company_value(ticker, growth_rate, wacc, years)
        company_values.append(company_value)
        market_prices.append(market_price)

        capital_gains = capital_gains_yield(market_price, company_value)
        div_yield = dividend_yield(company_values[0] * growth_rate, market_price)  # Assume constant dividend growth
        total_return = expected_total_return(capital_gains, div_yield)

        print(f"Growth Rate: {growth_rate * 100}%")
        print(f"Estimated Company Value: ${company_value:.2f}")
        print(f"Capital Gains Yield: {capital_gains * 100:.2f}%")
        print(f"Dividend Yield: {div_yield * 100:.2f}%")
        print(f"Expected Total Return: {total_return * 100:.2f}%\n")

    plot_results(growth_rate_range, company_values, market_prices)


# Example Usage
ticker = "AAPL"  # Example: Apple Inc.
growth_rate_range = np.linspace(0.02, 0.10, 9)  # Growth rates from 2% to 10%
wacc = 0.08  # 8% Weighted Average Cost of Capital
years = 5  # Forecast period
tax_rate = 0.21

run_simulation(ticker, growth_rate_range, wacc, years)
