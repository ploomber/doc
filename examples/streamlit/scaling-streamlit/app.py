import streamlit as st


manual_polling = st.Page("manual_polling.py", title="Manual polling")
auto_polling = st.Page("auto_polling.py", title="Auto polling")
db_results = st.Page("db_results.py", title="DB Results")

pg = st.navigation([manual_polling, auto_polling, db_results])
st.set_page_config(page_title="Scaling a Streamlit app")
pg.run()
