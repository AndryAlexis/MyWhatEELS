import param

from .model import Model
from .view import View

class Controller(param.Parameterized):
    def __init__(self, model: Model, view: View):
        pass