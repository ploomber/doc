import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

headers = _get_websocket_headers()


header_name = headers.get("X-Auth-Name")
header_sub = headers.get("X-Auth-Sub")


st.write(header_name)
st.write(header_sub)

# link to logout
st.markdown('<a href="/exit" target="_self">Logout</a>', unsafe_allow_html=True)

if st.button("Print Message"):
    st.write("Button clicked. Here is your message!")
