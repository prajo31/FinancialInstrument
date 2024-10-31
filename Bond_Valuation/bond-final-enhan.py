import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Display Author Information
st.text("Prepared and Maintained by Dr. Joshi")
st.text("All Rights Reserved")

# Ensure the leaderboard table exists
def ensure_table_exists():
    """Create the leaderboard table if it doesn't exist."""
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

def get_db_connection():
    """Establish a database connection."""
    return sqlite3.connect('bond_data.db')

def save_entry(data):
    """Save a new bond entry to the leaderboard."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO leaderboard 
                     (student_name, company_name, cusip, yield, price, coupon_rate, 
                      settlement_date, maturity_date, face_value) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
    except Exception as e:
        st.error(f"Error saving entry to database: {e}")
    finally:
        conn.close()

def load_leaderboard():
    """Load the leaderboard data from the database."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM leaderboard ORDER BY price DESC", conn)
    conn.close()
    return df

# Initialize the leaderboard table
ensure_table_exists()

# Streamlit UI
st.title("Bond Valuation Simulation")
student_name = st.text_input("Student Name")
company_name = st.text_input("Company Name")
cusip = st.text_input("CUSIP Number")
face_value = st.number_input("Face Value", min_value=0.0)

# Initialize session state if not set
if "yield_rate" not in st.session_state:
    st.session_state["yield_rate"] = 5.0
if "coupon_rate" not in st.session_state:
    st.session_state["coupon_rate"] = 5.0

# Sidebar Sensitivity Analysis
st.sidebar.subheader("Sensitivity Analysis")

# Sliders and input fields are synchronized through session state
yield_slider = st.sidebar.slider(
    "Yield Rate (%)", min_value=0.0, max_value=20.0,
    value=st.session_state["yield_rate"],
    key="yield_slider",
    on_change=lambda: st.session_state.update({"yield_rate": st.session_state["yield_slider"]})
)

coupon_slider = st.sidebar.slider(
    "Coupon Rate (%)", min_value=0.0, max_value=20.0,
    value=st.session_state["coupon_rate"],
    key="coupon_slider",
    on_change=lambda: st.session_state.update({"coupon_rate": st.session_state["coupon_slider"]})
)

# Input fields that update slider values
yield_rate = st.number_input(
    "Yield (%)", min_value=0.0,
    value=st.session_state["yield_rate"],
    key="yield_rate",
    on_change=lambda: st.session_state.update({"yield_slider": st.session_state["yield_rate"]})
)

coupon_rate = st.number_input(
    "Coupon Rate (%)", min_value=0.0,
    value=st.session_state["coupon_rate"],
    key="coupon_rate",
    on_change=lambda: st.session_state.update({"coupon_slider": st.session_state["coupon_rate"]})
)

settlement_date = st.date_input("Settlement Date", value=datetime.today())
maturity_date = st.date_input("Maturity Date")
payment_frequency = st.selectbox("Payment Frequency", options=["Annual", "Semiannual", "Quarterly"])

frequency_map = {"Annual": 1, "Semiannual": 2, "Quarterly": 4}
frequency = frequency_map[payment_frequency]

def calculate_bond_price(face_value, coupon_rate, yield_rate, settlement_date, maturity_date, frequency):
    """Calculate the bond price based on inputs."""
    settlement_date = pd.to_datetime(settlement_date)
    maturity_date = pd.to_datetime(maturity_date)
    days_to_maturity = (maturity_date - settlement_date).days
    N = days_to_maturity / 360
    coupon_payment = face_value * (coupon_rate / 100) / frequency
    total_payments = int(N * frequency)
    pv_coupons = sum(
        coupon_payment / (1 + yield_rate / 100 / frequency) ** (f + 1) for f in range(total_payments)
    )
    pv_face_value = face_value / (1 + yield_rate / 100 / frequency) ** total_payments
    bond_price = pv_coupons + pv_face_value
    return round(bond_price, 2)

if st.button("Calculate Price"):
    # Validate dates
    if maturity_date <= settlement_date:
        st.error("Maturity date must be after the settlement date.")
    else:
        price = calculate_bond_price(face_value, coupon_rate, yield_rate, settlement_date, maturity_date, frequency)
        st.write(f"The calculated bond price is: **${price:.2f}**")
        save_entry((student_name, company_name, cusip, yield_rate, price, coupon_rate,
                     settlement_date.strftime('%m-%d-%Y'), maturity_date.strftime('%m-%d-%Y'), face_value))
        st.success("Entry saved to the leaderboard!")

# Load and filter leaderboard
leaderboard = load_leaderboard()
min_coupon, max_coupon = st.slider(
    "Select Coupon Rate Range", min_value=0.0, max_value=10.0, value=(0.0, 10.0)
)
filtered_data = leaderboard[
    (leaderboard['coupon_rate'] >= min_coupon) & (leaderboard['coupon_rate'] <= max_coupon)
]

# Control visualization type
if st.button("Show Leaderboard"):
    st.session_state["show_leaderboard"] = True

if st.button("Show Heatmap"):
    st.session_state["show_heatmap"] = True

if st.button("Show Scatter Plot"):
    st.session_state["show_scatter"] = True

# Display Leaderboard
if st.session_state.get("show_leaderboard", False):
    st.subheader("Leaderboard")
    st.dataframe(leaderboard)

# Display Heatmap
if st.session_state.get("show_heatmap", False):
    pivot_table = filtered_data.pivot_table(values='price', index='yield', columns='coupon_rate', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_table, cmap='YlGnBu', annot=True, fmt=".2f", ax=ax)
    ax.set_title("Average Bond Price: Yield vs Coupon Rate")
    ax.set_xlabel("Coupon Rate (%)")
    ax.set_ylabel("Yield (%)")
    st.pyplot(fig)

# Display Scatter Plot
if st.session_state.get("show_scatter", False):
    # Calculate years to maturity for the entire leaderboard
    leaderboard['years_to_maturity'] = (pd.to_datetime(leaderboard['maturity_date']) - datetime.now()).dt.days / 365

    if leaderboard.empty:
        st.warning("No data to display in scatter plot.")
    else:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        scatter = ax.scatter(
            leaderboard['years_to_maturity'],
            leaderboard['coupon_rate'],
            leaderboard['yield'],
            c=leaderboard['price'],
            s=leaderboard['yield'] * 10,
            cmap='viridis',
            alpha=0.6,
            edgecolors='w'
        )

        cbar = plt.colorbar(scatter)
        cbar.set_label('Bond Price ($)')
        ax.set_xlabel('Years to Maturity')
        ax.set_ylabel('Coupon Rate (%)')
        ax.set_zlabel('Yield Rate (%)')
        ax.set_title('Scatter Plot of Bond Price vs Coupon Rate vs Yield vs Years to Maturity')
        st.pyplot(fig)

# Reset Leaderboard Data with Confirmation
if st.button("Refresh Data"):
    if 'confirm_delete' not in st.session_state:
        st.session_state['confirm_delete'] = True
        st.warning("Please confirm deletion. Press again to delete all entries.")
    else:
        conn = get_db_connection()
        conn.execute("DELETE FROM leaderboard")
        conn.commit()
        conn.close()
        st.success("All entries have been deleted!")
        st.session_state['confirm_delete'] = False  # Reset confirmation
        st.session_state["show_leaderboard"] = False
        st.session_state["show_heatmap"] = False
        st.session_state["show_scatter"] = False
