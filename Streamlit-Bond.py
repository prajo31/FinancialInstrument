import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Function to calculate bond price
def calculate_price(face_value, market_rate, years, coupon_rate):
    """Calculate the bond price."""
    C = face_value * coupon_rate  # Annual coupon payment
    F = face_value  # Face value (principal)

    # Present value of coupons
    pv_coupons = sum(C / (1 + market_rate) ** t for t in range(1, years + 1))

    # Present value of face value (principal)
    pv_face_value = F / (1 + market_rate) ** years

    return pv_coupons + pv_face_value


# Function to update all plots and the table
def update_visualizations(face_value, ytm_range, years_range, coupon_rate_range):
    # Generate ranges for YTM, years, and coupon rate
    rates = np.arange(ytm_range[0], ytm_range[1] + 0.5, 0.5) / 100  # YTM range (in decimal)
    years = np.arange(years_range[0], years_range[1] + 1)  # Years to maturity range
    coupon_rates = np.linspace(coupon_rate_range[0], coupon_rate_range[1], 5) / 100  # Coupon rate range (in decimal)

    # Prepare data for the DataFrame
    data = []

    # Loop through all combinations of rates, years, and coupon rates
    for r in rates:  # Loop through YTM values
        for y in years:  # Loop through years to maturity
            for cr in coupon_rates:  # Loop through coupon rates
                price = calculate_price(face_value, r, y, cr)
                data.append([r * 100, y, cr * 100, price])  # YTM and coupon rate in percentage for display

    # Display DataFrame
    df = pd.DataFrame(data, columns=["YTM (%)", "Years to Maturity", "Coupon Rate (%)", "Bond Price"]).sort_values(by="Coupon Rate (%)", ascending=False)
    st.write("### Impact of Market Rate, Coupon Rate, and Maturity on Bond Price")
    st.dataframe(df)

    # 3D Plot Section
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Create meshgrid for 3D plot
    R, Y = np.meshgrid(rates * 100, years)  # Multiply rates by 100 for percentage representation
    Z = np.zeros((len(years), len(rates)))

    for i, y in enumerate(years):
        for j, r in enumerate(rates):
            # Calculate bond price for each combination of years and market rate
            # Use a fixed coupon rate, or average it for simplicity in the plot
            Z[i, j] = calculate_price(face_value, r, y, np.mean(coupon_rates))  # Average coupon rate for surface plot

    # Plot the 3D surface
    surf = ax.plot_surface(R, Y, Z, cmap='viridis')

    # Set axis labels and title
    ax.set_xlabel("Market Rate (YTM) %")
    ax.set_ylabel("Years to Maturity")
    ax.set_zlabel("Bond Price")
    ax.set_title("3D Plot: Impact of Market Rate, Years, and Coupon Rate on Bond Price")

    # Display the 3D plot in Streamlit
    st.pyplot(fig)

    # Line Plot Section: Impact of YTM, Coupon Rate, and Years on Price
    st.write("### Line Plots for Detailed Impact")
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))

    # Plot: Impact of YTM on Bond Price for fixed coupon rate and maturity
    for cr in coupon_rates:
        prices = [calculate_price(face_value, r, 10, cr) for r in rates]  # Fixed maturity of 10 years
        ax[0].plot(rates * 100, prices, label=f"Coupon Rate {cr * 100:.1f}%")
    ax[0].set_xlabel("YTM (%)")
    ax[0].set_ylabel("Bond Price")
    ax[0].legend()
    ax[0].set_title("Impact of YTM on Bond Price (10 Years Maturity)")

    # Plot: Impact of Coupon Rate on Bond Price for fixed YTM and maturity
    for r in rates:
        prices = [calculate_price(face_value, r, 10, cr) for cr in coupon_rates]  # Fixed maturity of 10 years
        ax[1].plot(coupon_rates * 100, prices, label=f"YTM {r * 100:.1f}%")
    ax[1].set_xlabel("Coupon Rate (%)")
    ax[1].set_ylabel("Bond Price")
    ax[1].legend()
    ax[1].set_title("Impact of Coupon Rate on Bond Price (10 Years Maturity)")

    # Plot: Impact of Years to Maturity on Bond Price for fixed YTM and coupon rate
    for cr in coupon_rates:
        prices = [calculate_price(face_value, 0.05, y, cr) for y in years]  # Fixed coupon rate of 5%
        ax[2].plot(years, prices, label=f"Coupon Rate {cr * 100:.1f}%")
    ax[2].set_xlabel("Years to Maturity")
    ax[2].set_ylabel("Bond Price")
    ax[2].legend()
    ax[2].set_title("Impact of Maturity on Bond Price (Fixed Coupon Rate)")

    # Display the line plots in Streamlit
    st.pyplot(fig)


# Streamlit Sidebar for User Inputs
st.sidebar.title("Bond Parameters")
face_value = st.sidebar.number_input("Face Value", value=1000, step=50)  # Increment by 50
ytm_range = st.sidebar.slider("YTM / Market Rate (%)", 1.0, 15.0, (1.0, 10.0), step=0.5)
years_range = st.sidebar.slider("Years to Maturity", 1, 30, (1, 10), step=1)
coupon_rate_range = st.sidebar.slider("Coupon Rate (%)", 1.0, 10.0, (1.0, 5.0), step=0.5)

# Call the update_visualizations function with user inputs
update_visualizations(face_value, ytm_range, years_range, coupon_rate_range)
