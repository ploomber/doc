import streamlit as st

headers = st.context.headers


header_name = headers.get("X-Auth-Name")
header_sub = headers.get("X-Auth-Sub")
header_id_token = headers.get("X-Id-Token")
header_access_token = headers.get("X-Access-Token")

st.write(header_name)
st.write(header_sub)
st.write("Got ID token!" if header_id_token else "No ID token")
st.write("Got Access token!" if header_access_token else "No Access token")

# link to logout
st.markdown('<a href="/exit" target="_self">Logout</a>', unsafe_allow_html=True)

if st.button("Print Message"):
    st.write("Button clicked. Here is your message!")
