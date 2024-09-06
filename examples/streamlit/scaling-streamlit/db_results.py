import streamlit as st
from tasks import manager


st.title("DB Results")

user_id = st.text_input("User ID:", key="user_id_input")

if st.button("Get results"):
    df = manager.get_user_results(user_id)
    st.dataframe(df)
