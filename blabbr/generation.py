# -*- coding: UTF-8 -*-

from random import random

from blabbr import text as tx


class Generator:
    """
    A random tweets generator.
    """

    def __init__(self, model):
        self.model = model

    def tweets(self, count=20, min_length=50):
        n = 0
        while n < count:
            t = self.model.make_tweet()
            if not t:
                continue

            if not self._tweet_ok(t, min_length):
                continue

            yield self.decorate_tweet(t)
            n += 1

    def decorate_tweet(self, text):
        # Remove spaces around punctuation. This may vary per language
        text = tx.fix_punctuation(text)

        if len(text) < 138 and text[-1] not in "?!.":
            if random() > 0.9:
                bang = "!" if random() > 0.1 else "!!"
                text = "%s %s" % (text, bang)
        return text

    def tweet(self, min_length=50):
        for t in self.tweets(1, min_length=min_length):
            return t

    def _tweet_ok(self, t, min_length=50):
        _forbidden_terms = (
            # FR
            "tuer", "mort", "suicid", "bombe", "encul",
        )

        if len(t) < min_length:
            return False

        lt = t.lower()

        for term in _forbidden_terms:
            if term in lt:
                return False

        return True
