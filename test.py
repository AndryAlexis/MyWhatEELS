import panel as pn

from panel.reactive import ReactiveHTML

pn.extension()

class Slideshow(ReactiveHTML):
    _template = """

    <img id="testing" src="https://upload.wikimedia.org/wikipedia/commons/c/ca/1x1.png" onload="${_handle_reload}" />

    <script>
        document.body.addEventListener('beforeunload', function(event) {
            ${_handle_before_unload}
        });
    </script>

    """

    def _handle_reload(self, event):
        print("Page reload detected!")

    def _handle_before_unload(self, event):
        print("Page unload detected!")

pn.serve(Slideshow(), port=5011, show=True)