import streamlit as st
import tasks
import functions

st.title("Auto Polling")

st.write("Optionally enter a user ID to store status and results in the database.")

user_id = st.text_input("User ID:", key="user_id_input")

if st.button("Run expensive computation"):
    result = tasks.run_until_complete(functions.expensive_computation, user_id=user_id)
    st.write(f"Result: {result}")
