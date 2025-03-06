import streamlit as st
import pandas as pd
import os
import random
import sqlite3
import matplotlib.pyplot as plt

# Display Author Information
st.text("Prepared and Maintained by Dr. Joshi")
st.text("All Rights Reserved")

# Database file
DB_FILE = 'leaderboard.db'


# Function to create a connection to the SQLite database
def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn


# Function to initialize the leaderboard table
def initialize_db():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                calculation_type TEXT NOT NULL,
                input_value REAL NOT NULL,
                result REAL NOT NULL,
                years INTEGER NOT NULL,
                rate REAL NOT NULL,
                news TEXT NOT NULL
            )
        ''')
    conn.close()


# Clear the leaderboard
def clear_leaderboard():
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM leaderboard')
    conn.close()


# Load the leaderboard data from the SQLite database
def load_leaderboard():
    conn = create_connection()
    df = pd.read_sql_query('SELECT * FROM leaderboard', conn)
    conn.close()
    return df


# Save the leaderboard data to the SQLite database
def save_to_leaderboard(name, calculation_type, input_value, result, years, rate, news):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO leaderboard (name, calculation_type, input_value, result, years, rate, news)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, calculation_type, input_value, result, years, rate, news))
    conn.close()


# Display the global leaderboard
def display_global_leaderboard():
    df = load_leaderboard()
    if not df.empty:
        st.write("\n--- Global Leaderboard ---")
        st.dataframe(df)
    else:
        st.write("\n--- Global Leaderboard ---")
        st.write("No entries yet.")


# Define economic scenarios with corresponding interest rates ranges and news
economic_scenarios = {
    "Low Unemployment": (random.uniform(0.10, 0.15), "The economy is thriving with low unemployment rates."),
    "Stable Economy": (random.uniform(0.05, 0.10), "The economy is stable with consistent growth."),
    "Moderate Inflation": (random.uniform(0.05, 0.08), "Inflation is moderate, affecting purchasing power."),
    "Recession": (random.uniform(0.02, 0.05), "The economy is in recession with rising unemployment."),
    "High Inflation": (random.uniform(0.05, 0.08), "High inflation is affecting consumer prices significantly."),
    "Boom": (random.uniform(0.13, 0.18), "The economy is booming with significant growth."),
    "World at War": (random.uniform(0.01, 0.03), "The world is in conflict, leading to high oil prices."),
}


# TVM class for calculations
class TVM:
    def __init__(self, rate, periods):
        self.rate = rate
        self.periods = periods

    def future_value(self, present_value):
        return present_value * (1 + self.rate) ** self.periods

    def present_value(self, future_value):
        return future_value / (1 + self.rate) ** self.periods

    def future_value_annuity(self, payment):
        return payment * (((1 + self.rate) ** self.periods - 1) / self.rate)

    def present_value_annuity(self, payment):
        return payment * (1 - (1 + self.rate) ** -self.periods) / self.rate


# Streamlit app
def main():
    initialize_db()  # Initialize the database and table
    st.title("💰 Time Value of Money Simulation")
    st.markdown("## Welcome to the Simulation")
    st.markdown("**Use this app to understand financial concepts effectively!**")

    # Help Sidebar
    st.sidebar.header("Help")
    st.sidebar.markdown("""
    ### How to Use This App
    1. **Enter your name** to personalize your experience.
    2. **Input values** for present value, future value, or annuity payment. You can enter 0 if not applicable.
    3. **Adjust the Interest Rate** and **Number of Years** using the sliders.
    4. Click **Submit** to see your results and display them on the leaderboard.
    5. Use the **Clear Leaderboard** button if you want to reset the entries.
    """)

    # Clear the leaderboard if needed
    if st.button("Clear Leaderboard"):
        clear_leaderboard()
        st.success("Leaderboard cleared!")

    # Session state initialization
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'rate' not in st.session_state:
        scenario = random.choice(list(economic_scenarios.items()))
        st.session_state.rate = scenario[1][0]
        st.session_state.selected_scenario = scenario[0]
        st.session_state.news = scenario[1][1]
    if 'periods' not in st.session_state:
        st.session_state.periods = 10

    # Display the selected economic scenario
    st.markdown(f"### Economic Scenario: **{st.session_state.selected_scenario}**")
    st.markdown(f"**News:** {st.session_state.news}")

    # User input for name and calculations
    st.session_state.student_name = st.text_input("Enter your name:", st.session_state.student_name)
    present_value = st.number_input("Enter present value (or 0 if not applicable):", 0.0)
    future_value = st.number_input("Enter future value (or 0 if not applicable):", 0.0)
    payment_annuity = st.number_input("Enter annuity payment (or 0 if not applicable):", 0.0)

    # Additional Sliders for Rate and Years
    rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=20.0,
                     value=st.session_state.rate * 100) / 100  # Convert to decimal
    periods = st.slider("Number of Years", min_value=1, max_value=50, value=st.session_state.periods)

    # Update the session state with the latest rate and periods
    st.session_state.rate = rate
    st.session_state.periods = periods

    # Check if the user has already submitted an entry
    leaderboard = load_leaderboard()
    user_exists = leaderboard[leaderboard['name'].str.lower() == st.session_state.student_name.lower()]

    # Recalculate and display results dynamically
    tvm = TVM(st.session_state.rate, st.session_state.periods)

    if present_value > 0:
        fv_result = tvm.future_value(present_value)
        st.markdown(f"### Future Value: **${fv_result:.2f}**")
    else:
        fv_result = None

    if future_value > 0:
        pv_result = tvm.present_value(future_value)
        st.markdown(f"### Present Value: **${pv_result:.2f}**")
    else:
        pv_result = None

    if payment_annuity > 0:
        fv_annuity_result = tvm.future_value_annuity(payment_annuity)
        st.markdown(f"### Future Value of Annuity: **${fv_annuity_result:.2f}**")

        pv_annuity_result = tvm.present_value_annuity(payment_annuity)
        st.markdown(f"### Present Value of Annuity: **${pv_annuity_result:.2f}**")
    else:
        fv_annuity_result = pv_annuity_result = None

    # Submit button logic
    if st.button("Submit") and user_exists.empty:
        if fv_result is not None:
            save_to_leaderboard(st.session_state.student_name, 'Future Value', present_value, fv_result, periods,
                                st.session_state.rate, st.session_state.news)

        if pv_result is not None:
            save_to_leaderboard(st.session_state.student_name, 'Present Value', future_value, pv_result, periods,
                                st.session_state.rate, st.session_state.news)

        if fv_annuity_result is not None:
            save_to_leaderboard(st.session_state.student_name, 'Future Value of Annuity', payment_annuity,
                                fv_annuity_result, periods, st.session_state.rate, st.session_state.news)

        if pv_annuity_result is not None:
            save_to_leaderboard(st.session_state.student_name, 'Present Value of Annuity', payment_annuity,
                                pv_annuity_result, periods, st.session_state.rate, st.session_state.news)

        # Display global leaderboard
        display_global_leaderboard()
    elif not user_exists.empty:
        st.warning("You have already submitted your entry.")

    # Visualization for Future and Present Value
    if fv_result is not None and pv_result is not None:
        # Bar Chart for Future Value and Present Value
        fig, ax = plt.subplots()
        ax.bar(['Future Value', 'Present Value'], [fv_result, pv_result], color=['blue', 'orange'])
        ax.set_ylabel('Amount ($)')
        ax.set_title('Future Value vs Present Value')
        # Add values on top of bars
        for i, v in enumerate([fv_result, pv_result]):
            ax.text(i, v + 0.05 * max(fv_result, pv_result), f"${v:.2f}", ha='center')

        st.pyplot(fig)  # Display the chart in Streamlit

    # Sensitivity Analysis Table
    st.markdown("### Sensitivity Analysis")
    sensitivity_data = {
        "Interest Rate (%)": [],
        "Years": [],
        "Future Value": [],
        "Present Value": []
    }

    for r in range(1, 21, 5):  # Adjusting the rate from 1% to 20% in steps of 5%
        for y in range(1, 51, 10):  # Adjusting years from 1 to 50 in steps of 10
            tvm = TVM(r / 100, y)
            sensitivity_data["Interest Rate (%)"].append(r)
            sensitivity_data["Years"].append(y)
            sensitivity_data["Future Value"].append(tvm.future_value(present_value) if present_value > 0 else None)
            sensitivity_data["Present Value"].append(tvm.present_value(future_value) if future_value > 0 else None)

    sensitivity_df = pd.DataFrame(sensitivity_data)
    st.dataframe(sensitivity_df)

    # Display the global leaderboard
    display_global_leaderboard()

# Run the Streamlit app
if __name__ == "__main__":
    main()
