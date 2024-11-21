# Dash SAML authentication

> [!CAUTION]
> IMPORTANT: This is a simplified example for demonstration purposes only.
> 
> Security Warning:
> - This code lacks several crucial security features and should NOT be used in a production environment as-is.
> - Implement proper security measures, including but not limited to: input validation, error handling, secure session management, and protection against common web vulnerabilities (XSS, CSRF, etc.).

---

For an in depth explanation, please visit [the related blog post](https://ploomber.io/blog/dash-saml/)

To start the service:

1. Add your `Identity Provider Certificate` from auth0, as `key.pem` to this folder

2. Add your `AUTH0_CLIENT_ID` and `AUTH0_ENTITY_ID` in ./server.py

3. In the Settings of SAML2, on Auth0, add the following settings
    ```json
    {
      "logout": {
        "callback": "http://localhost:8050/sls",
        "slo_enabled": true
      }
    }
    ```

4. Install the dependencies
    ```sh
    pip install -r requirements.txt
    ```

5. Start the application
    ```sh
    python app.py
    ```
___

**⚠️ Important**

This implementation serves as an educational example to demonstrate SAML integration with Streamlit. It intentionally omits several critical security measures required for production environments. SAML, being an XML-based protocol, requires careful security configuration to prevent vulnerabilities.

### Professional Alternative

Rather than implementing SAML authentication from scratch, consider using a managed service that handles authentication for your deployed applications. At Ploomber, we offer enterprise-grade authentication as part of our Teams license for Ploomber Cloud.

Our managed authentication solution supports:
- Streamlit applications
- Dash applications
- Docker containers
- And more!

With our solution, there's no need to modify your app's source code. We handle the complexities of SAML authentication in prior of the user reaching your application, and that with your IdP, ensuring a secure and seamless with your work place.

[Contact us to learn more about](https://ploomber.io/contact/)
