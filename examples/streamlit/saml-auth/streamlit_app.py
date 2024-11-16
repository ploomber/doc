import streamlit as st
import requests

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

# Check for authentication token
if 'auth_token' in st.query_params and not st.session_state.authenticated:
    # Validate token with Flask server
    try:
        response = requests.get(
            'http://localhost:5000/validate_token',
            params={'token': st.query_params.auth_token}
        )
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.session_state.user_info = response.json()
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Authentication failed. Please try logging in again.")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")

# Main application logic
if not st.session_state.authenticated:
    st.title("Welcome to My Streamlit App")
    if st.button("Login with SAML"):
        # Redirect to Flask server's login endpoint
        js = """
        <meta http-equiv="refresh" content="0;url=http://localhost:5000/login">
        """
        st.markdown(js, unsafe_allow_html=True)
else:
    st.title(f"Welcome {st.session_state.user_info.get('email', 'User')}")
    st.write("Your profile:", st.session_state.user_info)

    if st.sidebar.button("Logout"):
        # Include the token in the logout request
        token = st.session_state.user_info.get('session_index')
        js = f"""
        <meta http-equiv="refresh" content="0;url=http://localhost:5000/logout?token={token}">
        """
        st.markdown(js, unsafe_allow_html=True)
        st.session_state.authenticated = False
        st.session_state.user_info = None
