# -*- coding: UTF-8 -*-

from random import random

class Generator:
    def __init__(self, model):
        self.model = model

    def tweets(self, count=20, min_length=50):
        n = 0
        while n < count:
            t = self.model.make_short_sentence(140,
                    tries=100, max_overlap_ratio=0.5)
            if not t:
                continue

            if not self._tweet_ok(t, min_length):
                continue

            if len(t) < 138 and t[-1] not in "?!.":
                if random() > 0.9:
                    bang = "!" if random() > 0.1 else "!!"
                    t = "%s %s" % (t, bang)

            yield t
            n += 1

    def tweet(self, min_length=50):
        for t in self.tweets(1, min_length=min_length):
            return t

    def _tweet_ok(self, t, min_length=50):
        _forbidden_terms = (
            "faut tuer", "à mort", "suicid", "bombe",
        )

        if len(t) < min_length:
            return False

        lt = t.lower()

        for term in _forbidden_terms:
            if term in lt:
                return False

        return True
