import streamlit as st
import pandas as pd
import os

# File to store leaderboard data
LEADERBOARD_FILE = 'leaderboard.csv'

# Function to clear the leaderboard
def clear_leaderboard():
    # Create a new empty DataFrame
    df = pd.DataFrame(columns=['name', 'calculation_type', 'input_value', 'result', 'years', 'rate'])
    df.to_csv(LEADERBOARD_FILE, index=False)

# Load the leaderboard data from the CSV file
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        return pd.read_csv(LEADERBOARD_FILE)
    return pd.DataFrame(columns=['name', 'calculation_type', 'input_value', 'result', 'years', 'rate'])

# Save the leaderboard data to the CSV file
def save_to_leaderboard(name, calculation_type, input_value, result, years, rate):
    # Load existing leaderboard data
    df = load_leaderboard()

    # Normalize the name to lowercase for case-insensitive comparison
    name = name.lower()

    # Remove previous entries for the same student and calculation type
    df = df[~((df['name'].str.lower() == name) & (df['calculation_type'] == calculation_type))]

    # Create a new entry
    new_entry = pd.DataFrame({
        'name': [name],
        'calculation_type': [calculation_type],
        'input_value': [input_value],
        'result': [result],
        'years': [years],
        'rate': [rate]
    })

    # Append the new entry to the DataFrame
    df = pd.concat([df, new_entry], ignore_index=True)

    # Save the updated DataFrame back to the CSV file, overwriting it
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
    st.title("Time Value of Money Simulation")

    # Clear the leaderboard if needed
    if st.button("Clear Leaderboard"):
        clear_leaderboard()
        st.success("Leaderboard cleared!")

    # Session state initialization
    if 'rate' not in st.session_state:
        st.session_state.rate = 0.05
    if 'periods' not in st.session_state:
        st.session_state.periods = 10
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'has_submitted' not in st.session_state:
        st.session_state.has_submitted = False  # Track if the user has submitted

    # Input for interest rate and periods
    st.session_state.rate = st.number_input("Enter the interest rate (as a decimal):", 0.0, 1.0, st.session_state.rate)
    st.session_state.periods = st.number_input("Enter the number of periods (years):", 1, 100, st.session_state.periods)
    st.session_state.student_name = st.text_input("Enter your name:", st.session_state.student_name)

    # Calculation inputs
    present_value = st.number_input("Enter present value (or 0 if not applicable):", 0.0)
    future_value = st.number_input("Enter future value (or 0 if not applicable):", 0.0)
    payment_annuity = st.number_input("Enter annuity payment (or 0 if not applicable):", 0.0)

    # Check if user has already submitted
    if st.session_state.has_submitted:
        st.warning("You have already submitted your entry. Please refresh to make a new entry.")
    else:
        if st.button("Submit"):
            # Perform calculations
            tvm = TVM(st.session_state.rate, st.session_state.periods)

            # Calculate and store results based on user inputs
            if present_value > 0:
                fv = tvm.future_value(present_value)
                save_to_leaderboard(st.session_state.student_name, 'Future Value', present_value, fv, st.session_state.periods, st.session_state.rate)
                st.write(f"Future Value: {fv:.2f}")

            if future_value > 0:
                pv = tvm.present_value(future_value)
                save_to_leaderboard(st.session_state.student_name, 'Present Value', future_value, pv, st.session_state.periods, st.session_state.rate)
                st.write(f"Present Value: {pv:.2f}")

            if payment_annuity > 0:
                fv_annuity = tvm.future_value_annuity(payment_annuity)
                save_to_leaderboard(st.session_state.student_name, 'Future Value of Annuity', payment_annuity, fv_annuity, st.session_state.periods, st.session_state.rate)
                st.write(f"Future Value of Annuity: {fv_annuity:.2f}")

                pv_annuity = tvm.present_value_annuity(payment_annuity)
                save_to_leaderboard(st.session_state.student_name, 'Present Value of Annuity', payment_annuity, pv_annuity, st.session_state.periods, st.session_state.rate)
                st.write(f"Present Value of Annuity: {pv_annuity:.2f}")

            # Mark the user as having submitted
            st.session_state.has_submitted = True

            # Display the global leaderboard after each entry
            display_global_leaderboard()

if __name__ == "__main__":
    main()
