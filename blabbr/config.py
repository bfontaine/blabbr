# -*- coding: UTF-8 -*-

import os.path
from configparser import ConfigParser

here = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(here, ".."))

DEFAULT_CONFIG = {
    "auth": {},
    "behavior": {
        "follow": True,
        "unfollow": True,
        "like": True,
        "retweet": True,
    },
    "seeds": {
        "screen_names": "",
    }
}

class Config:
    def __init__(self, location="$root/blabbr.cfg"):
        self.path = location.replace("$root", root)
        self.cfg = ConfigParser()
        self.set_defaults()
        self.load()

    def load(self):
        if not os.path.isfile(self.path):
            self.save()

        self.cfg.read(self.path)

    def save(self):
        with open(self.path, "w") as f:
            self.cfg.write(f)

    def set_defaults(self):
        for section, body in DEFAULT_CONFIG.items():
            if self.cfg.has_section(section):
                before = dict(self.cfg[section])
            else:
                self.cfg.add_section(section)
                before = {}

            merged = {}
            merged.update(body)
            merged.update(before)
            self.cfg[section] = merged

    def git_like_representation(self):
        lines = []
        for section, k, v in self:
            lines.append("%s.%s = %s" % (section, k, v))
        return "\n".join(lines)

    def get(self, section, name, **kw):
        return self.cfg.get(section, name, **kw)

    def set(self, section, name, value):
        self.cfg[section][name] = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

    def __iter__(self):
        for section in self.cfg:
            for k, v in self.cfg[section].items():
                yield (section, k, v)

    def set_auth(self, auth):
        self.cfg["auth"] = dict(auth)

    def get_auth(self):
        return dict(self.cfg["auth"])

    def seeds(self):
        return self.cfg["seeds"]
