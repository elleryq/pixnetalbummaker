from gaeo.controller import BaseController
from google.appengine.api import conf

class WelcomeController(BaseController):
    """The default Controller

    You could change the default route in main.py
    """
    def index(self):
        """The default method

        related to templates/welcome/index.html
        """
        app_version, current_config_version, development = conf._inspect_environment()
        self.development = development
