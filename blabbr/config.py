# -*- coding: UTF-8 -*-

import os.path
from configparser import ConfigParser

here = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(here, ".."))

class Config:
    def __init__(self, location="$root/blabbr.cfg"):
        self.path = location.replace("$root", root)
        self.cfg = ConfigParser()
        self.load()

    def load(self):
        if not os.path.isfile(self.path):
            self.save()

        self.cfg.read(self.path)

    def save(self):
        with open(self.path, "w") as f:
            self.cfg.write(f)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()
        pass

    def set_auth(self, auth):
        self.cfg["auth"] = dict(auth)

    def get_auth(self):
        self.cfg.setdefault("auth", {})
        return dict(self.cfg["auth"])

    def seeds(self):
        return self.cfg["seeds"]
