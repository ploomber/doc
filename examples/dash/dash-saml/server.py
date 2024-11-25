"""
IMPORTANT: This is a simplified example for demonstration purposes only.

Security Warning:
- This code lacks several crucial security features and should NOT be used in a production environment as-is.
- Implement proper security measures, including but not limited to: input validation, error handling, secure session management, and protection against common web vulnerabilities (XSS, CSRF, etc.).
"""
from flask import Flask, request, redirect, session, jsonify, url_for, make_response
import json
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import os
from urllib.parse import urlparse
from werkzeug.middleware.proxy_fix import ProxyFix

server = Flask(__name__)
server.config['SECRET_KEY'] = os.urandom(24)
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

APP_URL = "http://localhost:8050"

# Config
AUTH0_CLIENT_ID = "[**YOUR_CLIENT_ID**]"
AUTH0_ENTITY_ID = "[**YOUR_ENTITY_ID**]"

# Cookie configuration
COOKIE_NAME = 'auth_data'
COOKIE_MAX_AGE = 3600  # 1 hour


def read_cert_from_file(filename):
    with open(filename, 'r') as cert_file:
        return cert_file.read().strip()


def get_saml_settings():
    return {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": f"{APP_URL}/metadata",
            "assertionConsumerService": {
                "url": f"{APP_URL}/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{APP_URL}/sls",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
        },
        "idp": {
            "entityId": f"urn:{AUTH0_ENTITY_ID}",
            "singleSignOnService": {
                "url": f"https://{AUTH0_ENTITY_ID}/samlp/{AUTH0_CLIENT_ID}",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"https://{AUTH0_ENTITY_ID}/samlp/{AUTH0_CLIENT_ID}/logout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": read_cert_from_file('./key.pem')
        }
    }


def prepare_flask_request():
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': request.query_string.decode('utf-8')
    }


@server.route('/metadata')
def metadata():
    auth = OneLogin_Saml2_Auth(prepare_flask_request(), get_saml_settings())
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        return metadata, 200, {'Content-Type': 'text/xml'}

    return "Error: " + ', '.join(errors), 400


@server.route('/login')
def login():
    req = prepare_flask_request()
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    return redirect(auth.login())


@server.route('/acs', methods=['POST'])
def acs():
    """ Assertion Consumer Service: Process the SAML response & redirect the user back to Streamlit """
    req = prepare_flask_request()
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    auth.process_response()
    errors = auth.get_errors()

    if not errors:
        if auth.is_authenticated():
            samlUserdata = auth.get_attributes()
            samlNameId = auth.get_nameid()
            samlSessionIndex = auth.get_session_index()

            # Prepare user data for cookie
            user_data = {
                'email': samlNameId,
                'attributes': samlUserdata,
                'session_index': samlSessionIndex
            }

            # Create response with redirect
            response = make_response(redirect(APP_URL))

            # Set secure cookie with user data
            response.set_cookie(
                COOKIE_NAME,
                json.dumps(user_data),
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                secure=True,
                samesite='Lax'
            )

            return response

    return f"Error: {', '.join(errors)}", 400


@server.route('/user')
def user():
    # Get the cookie
    auth_cookie = request.cookies.get(COOKIE_NAME)

    if auth_cookie:
        try:
            # Parse the JSON data from the cookie
            user_data = json.loads(auth_cookie)

            # Extract user information
            email = user_data.get('email', 'N/A')
            attributes = user_data.get('attributes', {})
            session_index = user_data.get('session_index', 'N/A')

            # Create a response with user information
            response = f"""
            <h1>Welcome, {email}!</h1>
            <h2>Your SAML Attributes:</h2>
            <ul>
            {"".join(f"<li>{key}: {value}</li>" for key, value in attributes.items())}
            </ul>
            <p>Session Index: {session_index}</p>
            <a href="/logout">Logout</a>
            """

            return response

        except json.JSONDecodeError:
            return "Error: Invalid auth cookie", 400

    else:
        return redirect(url_for('login'))


@server.route('/logout')
def logout():
    """ Single Logout Service: Process the SAML Response & logout the user """
    req = prepare_flask_request()
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    auth_data = request.cookies.get(COOKIE_NAME)

    if auth_data:
        try:
            user_data = json.loads(auth_data)
            name_id = user_data['email']
            session_index = user_data['session_index']

            response = make_response(redirect(auth.logout(
                name_id=name_id,
                session_index=session_index,
                return_to=url_for('sls', _external=True),
            )))
            response.delete_cookie(COOKIE_NAME)
            return response
        except json.JSONDecodeError:
            pass
    return redirect(f'{APP_URL}/')


@server.route('/sls', methods=['POST'])
def sls():
    req = prepare_flask_request()
    # INFO: process_slo expect a GET, but auth0 return a POST
    req["get_data"], req["post_data"] = req["post_data"], req["get_data"]
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())

    url = auth.process_slo(
        delete_session_cb=lambda: session.clear()
    )
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            return redirect(url)
        return redirect(f'{APP_URL}/')
    return "Error: " + ', '.join(errors), 400

