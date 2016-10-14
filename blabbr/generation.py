# -*- coding: UTF-8 -*-

import re
from random import random

import nltk
import markovify

from blabbr.config import root

# from https://github.com/jsvine/markovify#extending-markovifytext
class POSifiedText(markovify.NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = [ "::".join(tag) for tag in nltk.pos_tag(words) ]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

class Generator:
    def __init__(self):
        with open("%s/texts.txt" % root) as f:
            self.model = POSifiedText(f.read())

    def tweets(self, count=20, min_length=50):
        n = 0
        while n < count:
            t = self.model.make_short_sentence(140,
                    tries=100, max_overlap_ratio=0.5)
            if not t:
                continue

            if not tweet_ok(t, min_length):
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

_forbidden_terms = (
    "faut tuer", "à mort", "suicid", "bombe",
)

def tweet_ok(t, min_length=50):
    if len(t) < min_length:
        return False

    lt = t.lower()

    for term in _forbidden_terms:
        if term in lt:
            return False


    return True
