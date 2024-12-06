from apps import create_apps
import panel as pn

pn.extension(sizing_mode="stretch_width")

if __name__ == "__main__":
    apps = create_apps()
    pn.serve(apps, port=5006)