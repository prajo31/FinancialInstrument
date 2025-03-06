import streamlit as st
import pandas as pd
import os
import random
import matplotlib.pyplot as plt

# File to store leaderboard data
LEADERBOARD_FILE = 'leaderboard.csv'

# Function to clear the leaderboard
def clear_leaderboard():
    df = pd.DataFrame(columns=['name', 'calculation_type', 'input_value', 'result', 'years', 'rate', 'news'])
    df.to_csv(LEADERBOARD_FILE, index=False)

# Load the leaderboard data from the CSV file
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        return pd.read_csv(LEADERBOARD_FILE)
    return pd.DataFrame(columns=['name', 'calculation_type', 'input_value', 'result', 'years', 'rate', 'news'])

# Save the leaderboard data to the CSV file
def save_to_leaderboard(name, calculation_type, input_value, result, years, rate, news):
    df = load_leaderboard()
    new_entry = pd.DataFrame({
        'name': [name],
        'calculation_type': [calculation_type],
        'input_value': [input_value],
        'result': [result],
        'years': [years],
        'rate': [rate],
        'news': [news]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

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
    st.title("💰 Time Value of Money Simulation")
    st.markdown("## Welcome to the Simulation")
    st.markdown("**Use this app to understand financial concepts effectively!**")

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
    rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=20.0, value=st.session_state.rate * 100) / 100  # Convert to decimal
    periods = st.slider("Number of Years", min_value=1, max_value=50, value=st.session_state.periods)

    # Update the session state with the latest rate and periods
    st.session_state.rate = rate
    st.session_state.periods = periods

    # Check if the user has already submitted an entry
    leaderboard = load_leaderboard()
    user_exists = leaderboard[leaderboard['name'].str.lower() == st.session_state.student_name.lower()]

    if user_exists.empty:
        if st.button("Submit"):
            tvm = TVM(st.session_state.rate, st.session_state.periods)

            # Store results for visualization
            fv_result = pv_result = fv_annuity_result = pv_annuity_result = None

            if present_value > 0:
                fv_result = tvm.future_value(present_value)
                save_to_leaderboard(st.session_state.student_name, 'Future Value', present_value, fv_result, periods, st.session_state.rate, st.session_state.news)
                st.markdown(f"### Future Value: **{fv_result:.2f}**")

            if future_value > 0:
                pv_result = tvm.present_value(future_value)
                save_to_leaderboard(st.session_state.student_name, 'Present Value', future_value, pv_result, periods, st.session_state.rate, st.session_state.news)
                st.markdown(f"### Present Value: **{pv_result:.2f}**")

            if payment_annuity > 0:
                fv_annuity_result = tvm.future_value_annuity(payment_annuity)
                save_to_leaderboard(st.session_state.student_name, 'Future Value of Annuity', payment_annuity, fv_annuity_result, periods, st.session_state.rate, st.session_state.news)
                st.markdown(f"### Future Value of Annuity: **{fv_annuity_result:.2f}**")

                pv_annuity_result = tvm.present_value_annuity(payment_annuity)
                save_to_leaderboard(st.session_state.student_name, 'Present Value of Annuity', payment_annuity, pv_annuity_result, periods, st.session_state.rate, st.session_state.news)
                st.markdown(f"### Present Value of Annuity: **{pv_annuity_result:.2f}**")

            # Visualization for Future and Present Value
            if fv_result is not None and pv_result is not None:
                # Bar Chart for Future Value and Present Value
                fig, ax = plt.subplots()
                ax.bar(['Future Value', 'Present Value'], [fv_result, pv_result], color=['blue', 'orange'])
                ax.set_ylabel('Amount ($)')
                ax.set_title('Future Value vs Present Value')
                st.pyplot(fig)

            # Visualization for Annuity Results
            if fv_annuity_result is not None and pv_annuity_result is not None:
                # Bar Chart for Future Value of Annuity and Present Value of Annuity
                fig, ax = plt.subplots()
                ax.bar(['Future Value of Annuity', 'Present Value of Annuity'], [fv_annuity_result, pv_annuity_result], color=['green', 'red'])
                ax.set_ylabel('Amount ($)')
                ax.set_title('Annuity Results Comparison')
                st.pyplot(fig)

                st.markdown("""
                    ### Explanation of Annuity Results:
                    - **Future Value of Annuity**: This represents the total amount that will be accumulated after making regular annuity payments for a specified number of periods, given the interest rate.
                    - **Present Value of Annuity**: This shows how much a series of future annuity payments is worth today, considering the interest rate.
                """)

            # Effects of Interest Rates on PV and FV
            interest_rates = [i / 100 for i in range(1, 21)]  # 1% to 20%
            future_values = [TVM(rate, periods).future_value(present_value) for rate in interest_rates]
            present_values = [TVM(rate, periods).present_value(future_value) for rate in interest_rates]

            # Plotting the effect of interest rates on Future Value and Present Value
            fig, ax = plt.subplots()
            ax.plot(interest_rates, future_values, label='Future Value', color='blue', marker='o')
            ax.plot(interest_rates, present_values, label='Present Value', color='orange', marker='o')
            ax.set_xlabel('Interest Rate (%)')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Effect of Interest Rate on FV and PV')
            ax.legend()
            st.pyplot(fig)

            # Effects of Number of Years on FV and PV
            years = list(range(1, 21))  # 1 to 20 years
            future_values_years = [TVM(rate, year).future_value(present_value) for year in years]
            present_values_years = [TVM(rate, year).present_value(future_value) for year in years]

            # Plotting the effect of number of years on Future Value and Present Value
            fig, ax = plt.subplots()
            ax.plot(years, future_values_years, label='Future Value', color='blue', marker='o')
            ax.plot(years, present_values_years, label='Present Value', color='orange', marker='o')
            ax.set_xlabel('Number of Years')
            ax.set_ylabel('Amount ($)')
            ax.set_title('Effect of Number of Years on FV and PV')
            ax.legend()
            st.pyplot(fig)

            # Display the global leaderboard after each entry
            display_global_leaderboard()
    else:
        st.warning("You have already submitted your entry. Please refresh the page to see the leaderboard.")

    # Download leaderboard button
    if st.button("Download Leaderboard as CSV"):
        df = load_leaderboard()
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, "leaderboard.csv", "text/csv")

if __name__ == "__main__":
    main()
