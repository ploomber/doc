import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

headers = _get_websocket_headers()


header_name = headers.get("X-Auth-Name")
header_sub = headers.get("X-Auth-Sub")


st.write(header_name)
st.write(header_sub)


if st.button("Print Message"):
    st.write("Button clicked. Here is your message!")
