from wtforms import Form, BooleanField, StringField, PasswordField, validators


class SignUpForm(Form):
    email = StringField("Email Address", [validators.Length(min=6, max=35)])
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField(
        "I accept the terms of service", [validators.DataRequired()]
    )


class LoginForm(Form):
    email = StringField("Email Address", [validators.Length(min=6, max=35)])
    password = PasswordField("Password", [validators.DataRequired()])
