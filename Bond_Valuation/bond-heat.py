import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# --- Display Author Information ---
st.text("Prepared and Maintained by Dr. Joshi")
st.text("All Rights Reserved")


# Ensure the leaderboard table exists
def ensure_table_exists():
    conn = sqlite3.connect('bond_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
                    student_name TEXT,
                    company_name TEXT,
                    cusip TEXT,
                    yield REAL,
                    price REAL,
                    coupon_rate REAL,
                    settlement_date TEXT,
                    maturity_date TEXT,
                    face_value REAL
                )''')
    conn.commit()
    conn.close()


# Connect to SQLite database
def get_db_connection():
    return sqlite3.connect('bond_data.db')


# Save student entry to leaderboard
def save_entry(data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO leaderboard 
                 (student_name, company_name, cusip, yield, price, coupon_rate, 
                  settlement_date, maturity_date, face_value) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()


# Load leaderboard data
def load_leaderboard():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM leaderboard ORDER BY price DESC", conn)
    conn.close()
    return df


# Initialize the leaderboard table
ensure_table_exists()

# Initialize session state for visibility control
if "show_leaderboard" not in st.session_state:
    st.session_state["show_leaderboard"] = False
if "show_heatmap" not in st.session_state:
    st.session_state["show_heatmap"] = False
if "show_scatter" not in st.session_state:
    st.session_state["show_scatter"] = False

# Streamlit UI
st.title("Bond Valuation Simulation")

# User Input Form
student_name = st.text_input("Student Name")
company_name = st.text_input("Company Name")
cusip = st.text_input("CUSIP Number")
face_value = st.number_input("Face Value", min_value=0.0)
coupon_rate = st.number_input("Coupon Rate (%)", min_value=0.0)
yield_rate = st.number_input("Yield (%)", min_value=0.0)
settlement_date = st.date_input("Settlement Date", value=datetime.today())
maturity_date = st.date_input("Maturity Date")
payment_frequency = st.selectbox("Payment Frequency", options=["Annual", "Semiannual", "Quarterly"])

# Convert payment frequency to number of payments per year
frequency_map = {
    "Annual": 1,
    "Semiannual": 2,
    "Quarterly": 4
}
frequency = frequency_map[payment_frequency]


def calculate_bond_price(face_value, coupon_rate, yield_rate, settlement_date, maturity_date, frequency):
    # Convert dates to datetime objects
    settlement_date = pd.to_datetime(settlement_date)
    maturity_date = pd.to_datetime(maturity_date)

    # Calculate days to maturity using 30/360
    days_to_maturity = (maturity_date - settlement_date).days

    # Calculate number of years to maturity based on 30/360 convention
    N = days_to_maturity / 360

    # Annual coupon payment
    coupon_payment = face_value * (coupon_rate / 100) / frequency

    # Total number of coupon payments (using floor to get whole payments)
    total_payments = int(N * frequency)

    # Present value of coupon payments
    pv_coupons = sum(
        coupon_payment / (1 + yield_rate / 100 / frequency) ** (f + 1) for f in range(total_payments)
    )

    # Calculate present value of the face value at maturity
    pv_face_value = face_value / (1 + yield_rate / 100 / frequency) ** total_payments

    # Total bond price
    bond_price = pv_coupons + pv_face_value

    return round(bond_price, 2)



if st.button("Calculate Price"):
    price = calculate_bond_price(face_value, coupon_rate, yield_rate, settlement_date, maturity_date, frequency)
    st.write(f"The calculated bond price is: **${price:.2f}**")
    save_entry((student_name, company_name, cusip, yield_rate, price, coupon_rate, settlement_date.strftime('%m-%d-%Y'),
                maturity_date.strftime('%m-%d-%Y'), face_value))
    st.success("Entry saved to the leaderboard!")

# Load the leaderboard
leaderboard = load_leaderboard()

# Add Coupon Rate Filter
min_coupon, max_coupon = st.slider(
    "Select Coupon Rate Range", min_value=0.0, max_value=10.0, value=(0.0, 10.0)
)
filtered_data = leaderboard[
    (leaderboard['coupon_rate'] >= min_coupon) & (leaderboard['coupon_rate'] <= max_coupon)
    ]

# Control visualization type
if st.button("Show Leaderboard"):
    st.session_state["show_leaderboard"] = True
    st.session_state["show_heatmap"] = False
    st.session_state["show_scatter"] = False

if st.button("Show Heatmap"):
    st.session_state["show_heatmap"] = True
    st.session_state["show_leaderboard"] = False
    st.session_state["show_scatter"] = False

if st.button("Show Scatter Plot"):
    st.session_state["show_scatter"] = True
    st.session_state["show_leaderboard"] = False
    st.session_state["show_heatmap"] = False

# Display Leaderboard
if st.session_state["show_leaderboard"]:
    st.subheader("Leaderboard")
    st.dataframe(leaderboard)

# Display Heatmap
if st.session_state.get("show_heatmap"):
    pivot_table = filtered_data.pivot_table(values='price', index='yield', columns='coupon_rate', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_table, cmap='YlGnBu', annot=True, fmt=".2f", ax=ax)
    ax.set_title("Average Bond Price: Yield vs Coupon Rate")
    ax.set_xlabel("Coupon Rate (%)")
    ax.set_ylabel("Yield (%)")
    st.pyplot(fig)

# Display Scatter Plot
if st.session_state.get("show_scatter"):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(filtered_data['maturity_date'].apply(lambda x: (pd.to_datetime(x) - datetime.now()).days / 365),
               filtered_data['coupon_rate'],
               filtered_data['price'],
               c=filtered_data['yield'],
               cmap='viridis', marker='o')

    ax.set_xlabel('Years to Maturity')
    ax.set_ylabel('Coupon Rate (%)')
    ax.set_zlabel('Bond Price ($)')
    ax.set_title('Bond Price vs Years to Maturity and Coupon Rate')
    st.pyplot(fig)

# Reset Leaderboard Data
if st.button("Refresh Data"):
    conn = get_db_connection()
    conn.execute("DELETE FROM leaderboard")
    conn.commit()
    conn.close()
    st.success("All entries have been deleted!")
    st.session_state["show_leaderboard"] = False
    st.session_state["show_heatmap"] = False
    st.session_state["show_scatter"] = False
