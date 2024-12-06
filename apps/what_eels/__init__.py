# Import required Panel library and application components
import panel as pn
from .views import *
from .src.config.constants import *
from .src.utils.read_files import read_css

# Configure Panel extension with default sizing mode
pn.extension(sizing_mode="stretch_width")

def app():   
    # Dictionary mapping view names to view components
    views = {
        "Home page": home_view(),
        "About": about_view(),
    }

    def show(view):
        # Helper function to display selected view
        return views[view]

    # Get initial view from URL parameters, defaulting to Home page
    starting_view = pn.state.session_args.get("view", [b"Home page"])[0].decode()
        
    # Load custom CSS styling for radio buttons
    rb_stylesheet = read_css(path="apps/what_eels/src/styles/sidebar/radioButtonGroup.css")
    
    # Create radio button group for view selection
    radio_buttons = pn.widgets.RadioButtonGroup(
        value=starting_view,
        options=list(views.keys()),
        name="View",
        sizing_mode="fixed",
        button_type="success",
        orientation="vertical",
        stylesheets=[rb_stylesheet],
    )
        
    # Create sidebar containing radio buttons
    sidebar = pn.Column(
        radio_buttons,
    )

    # Bind view selection to radio buttons
    ishow = pn.bind(show, view=radio_buttons)

    # Sync URL parameter with selected view
    pn.state.location.sync(radio_buttons, {"value": "view"})
    
    # Return main application template
    return pn.template.FastListTemplate(
        title="",
        sidebar=[sidebar],
        main=[ishow],
        **DEFAULT_PARAMS,
        sidebar_width=225,
        raw_css=["""
            :host {
                border: 5px solid orange !important;
            }
            
            .card-margin.stretch_width {
                height: calc((100vh - 1em) - 80px);
            }
        """],
    )