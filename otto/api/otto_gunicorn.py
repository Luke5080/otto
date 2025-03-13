import multiprocessing
from gunicorn.app.base import BaseApplication
from exceptions import MultipleGunicornManager
from flask import Flask


class GunicornManager(BaseApplication):

    __instance = None
    @staticmethod
    def get_instance(app: Flask):
        if GunicornManager.__instance is None:
           GunicornManager(app)
        return GunicornManager.__instance

    def __init__(self, flask_app):
        if GunicornManager.__instance is None:
           self._app = flask_app
           self.host = "0.0.0.0"
           self.port = 5000
           self.options = {
             "bind": f"{self.host}:{self.port}",
             "workers": 1, # multiprocessing.cpu_count() * 2  maybe an overshoot
             "timeout": 180
             }

           super().__init__()

           GunicornManager.__instance = self
        else:
            raise MultipleGunicornManager(f"An occurence of GunicornManager already exists at {GunicornManager.__instance}")

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self._app
