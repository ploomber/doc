"""
IMPORTANT: This is a simplified example for demonstration purposes only.

Security Warning:
- This code lacks several crucial security features and should NOT be used in a production environment as-is.
- Implement proper security measures, including but not limited to: input validation, error handling, secure session management, and protection against common web vulnerabilities (XSS, CSRF, etc.).
"""
from flask import Flask, request, redirect, session, jsonify, url_for
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import requests
import os
from urllib.parse import urlparse
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Server-side token storage
valid_tokens = {}


# Note:
# - For a production-ready application, implement a reverse proxy setup:
#  - Use separate domains for the authentication server (e.g., auth.myapp.com)
#    and the Streamlit application (e.g., app.myapp.com).
#  - Configure the reverse proxy to route requests to the appropriate server
#    based on the domain.
STREAMLIT_SERVER_URL = "http://localhost:8501"
AUTH_PROXY_SERVER_URL = "http://localhost:5000"

# Config
AUTH0_CLIENT_ID = "[**REFACTED**]"
AUTH0_ENTITY_ID = "[**REFACTED**]"


def read_cert_from_file(filename):
    with open(filename, 'r') as cert_file:
        return cert_file.read().strip()


def get_saml_settings():
    return {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": f"{AUTH_PROXY_SERVER_URL}/metadata",
            "assertionConsumerService": {
                "url": f"{AUTH_PROXY_SERVER_URL}/acs",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"{AUTH_PROXY_SERVER_URL}/sls",
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


@app.route('/metadata')
def metadata():
    auth = OneLogin_Saml2_Auth(prepare_flask_request(), get_saml_settings())
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        return metadata, 200, {'Content-Type': 'text/xml'}

    return "Error: " + ', '.join(errors), 400


@app.route('/login')
def login():
    req = prepare_flask_request()
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    return redirect(auth.login())


@app.route('/acs', methods=['POST'])
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

            # Store as parameter for communication with Streamlit server
            token = samlSessionIndex
            valid_tokens[token] = {
                'email': samlNameId,
                'attributes': samlUserdata,
                'session_index': samlSessionIndex
            }

            # Redirect to Streamlit with authentication token (unsecure but valid for this demo)
            return redirect(f'{STREAMLIT_SERVER_URL}/?auth_token={samlSessionIndex}')

    return f"Error: {', '.join(errors)}", 400


@app.route('/validate_token')
def validate_token():
    token = request.args.get('token')
    if token and token in valid_tokens:
        return jsonify(valid_tokens[token])
    return jsonify({'error': 'Invalid token'}), 401


@app.route('/logout')
def logout():
    """ Single Logout Service: Process the SAML Response & logout the user """
    req = prepare_flask_request()
    auth = OneLogin_Saml2_Auth(req, get_saml_settings())
    token = request.args.get('token')

    if token and token in valid_tokens:
        name_id = valid_tokens[token]['email']
        session_index = token

        return redirect(auth.logout(
            name_id=name_id,
            session_index=session_index,
            return_to=url_for('sls', _external=True),
        ))
    return redirect(f'{STREAMLIT_SERVER_URL}/')


@app.route('/sls', methods=['POST'])
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
        return redirect(f'{STREAMLIT_SERVER_URL}/')
    return "Error: " + ', '.join(errors), 400


# Proxy all other requests to Streamlit

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    streamlit_url = f'{STREAMLIT_SERVER_URL}/{path}'
    resp = requests.request(
        method=request.method,
        url=streamlit_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = app.response_class(
        response=resp.content,
        status=resp.status_code,
        headers=headers)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
