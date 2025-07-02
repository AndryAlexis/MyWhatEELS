from whateels.components import CustomPage

class Login(CustomPage):
    """
    NLLS Page class for the WhatEELS application.
    This class extends CustomPage to create a specific NLLS page layout.
    """
    
    _DEFAULT_TITLE = "Login"
    _LOGIN_CSS_PATH = "whateels/assets/css/login.css"
    
    def __init__(self, title: str = _DEFAULT_TITLE):
        super().__init__(
            title=title,
            raw_css_path=self._LOGIN_CSS_PATH,
        )
        
        
# def login():
#     username = pn.widgets.TextInput(name="Username", placeholder="Enter your username")
#     password = pn.widgets.PasswordInput(name="Password", placeholder="Enter your password")
#     login_button = pn.widgets.Button(name="Login", button_type="primary")
#     login_message = pn.pane.Markdown("")

#     def authenticate(event):
#         # Simple hardcoded authentication for demonstration
#         if username.value == "admin" and password.value == "secret":
#             login_message.object = "✅ Login successful!"
#             # Here you could redirect or show the main app page
#         else:
#             login_message.object = "❌ Invalid credentials."

#     login_button.on_click(authenticate)
    

#     login_form = pn.Column(
#         pn.pane.Markdown("# Login"),
#         username,
#         password,
#         login_button,
#         login_message,
#         css_classes=["login-form"]
#     )
    
#     login_container = pn.Column(
#         login_form, 
#         sizing_mode="stretch_both", 
#         css_classes=["login-container"]
#     )

#     return login_container