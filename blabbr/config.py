# -*- coding: UTF-8 -*-

import os.path
from configparser import ConfigParser

FEATURES = ("follow", "unfollow", "like", "retweet")

DEFAULT_CONFIG = {
    "bot": {
        "lang": "en",
        "timezone": "Europe/Paris",
    },
    "auth": {
        "consumer_key": "",
        "consumer_secret": "",
        "token": "",
        "token_secret": "",
    },
    "seeds": {
        "screen_names": "",
    }
}

for f in FEATURES:
    DEFAULT_CONFIG["bot"][f] = True


class Config:
    DEFAULT_PATH = "blabbr.cfg"  # current directory

    LOOKUP_PATHS = (
        DEFAULT_PATH,
        os.path.expanduser("~/.blabbr.cfg")
    )

    def __init__(self, path):
        self.path = path
        self.cfg = ConfigParser()
        self.load()

    @classmethod
    def default(cls):
        for path in cls.LOOKUP_PATHS:
            if os.path.isfile(path):
                return cls(path)

        return cls(cls.DEFAULT_PATH)

    @classmethod
    def from_path(cls, path):
        if path is not None:
            return cls(os.path.expanduser(path))

        return cls.default()

    def load(self):
        if not os.path.isfile(self.path):
            self.set_defaults()
            self.save()
        else:
            self.cfg.read(self.path)
            self.set_defaults()

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
        return {k: v for k, v in self.cfg["auth"].items() if v}

    def enabled_features(self):
        feats = self.cfg["bot"]
        return {k: feats.getboolean(k, fallback=True) for k in FEATURES}
