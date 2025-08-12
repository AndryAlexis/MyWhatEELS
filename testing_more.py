import panel as pn
import datetime

pn.extension()

# Called when a new session/websocket is created (page reload or new tab)
def on_session_created(session_context):
    print("🔄 New session created! (Page reloaded or new tab)")
    print(f"Session ID: {id(session_context)} at {datetime.datetime.now()}")
    # You can put any reset logic here

# Called when a session/websocket is destroyed (user closes tab or disconnects)
def on_session_destroyed(session_context):
    print("❌ Session destroyed! (User closed tab or navigated away)")
    print(f"Session ID: {id(session_context)} at {datetime.datetime.now()}")

pn.state.on_session_created(on_session_created)
pn.state.on_session_destroyed(on_session_destroyed)

# Simple UI to show session info
def session_info():
    return pn.Column(
        pn.pane.Markdown(f"# Panel Session Demo"),
        pn.pane.Markdown(f"**Session ID:** {id(pn.state.curdoc)}"),
        pn.pane.Markdown(f"**Time:** {datetime.datetime.now().strftime('%H:%M:%S')}")
    )

pn.serve(session_info, port=5015, show=True)
