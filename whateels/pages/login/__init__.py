import panel as pn
pn.extension()
pn.config.raw_css.append(open("whateels/assets/css/login.css").read())

def login():
    username = pn.widgets.TextInput(name="Username", placeholder="Enter your username")
    password = pn.widgets.PasswordInput(name="Password", placeholder="Enter your password")
    login_button = pn.widgets.Button(name="Login", button_type="primary")
    login_message = pn.pane.Markdown("")

    def authenticate(event):
        # Simple hardcoded authentication for demonstration
        if username.value == "admin" and password.value == "secret":
            login_message.object = "✅ Login successful!"
            # Here you could redirect or show the main app page
        else:
            login_message.object = "❌ Invalid credentials."

    login_button.on_click(authenticate)
    

    login_form = pn.Column(
        pn.pane.Markdown("# Login"),
        username,
        password,
        login_button,
        login_message,
        css_classes=["login-form"]
    )
    
    login_container = pn.Column(
        login_form, 
        sizing_mode="stretch_both", 
        css_classes=["login-container"]
    )

    return login_container