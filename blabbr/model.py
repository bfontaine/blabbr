# -*- coding: UTF-8 -*-

import re
import json
import os.path

import nltk
import markovify
import markovify.text
from markovify.chain import Chain


# Simple format versionning
DUMP_FMT_VERSION = 1

# from https://github.com/jsvine/markovify#extending-markovifytext
class POSifiedText(markovify.Text):
    def __init__(self, input_text, state_size=2, chain=None):
        # Circumvent some limitations of markovify by allowing one to create a
        # POSifiedText from a markovify.Text instance
        if isinstance(input_text, markovify.Text):
            m = input_text
            self.input_text = m.input_text
            self.rejoined_text = m.rejoined_text
            self.chain = m.chain
            return

        super().__init__(input_text, state_size, chain)

    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = ["::".join((tag, word)) for word, tag in nltk.pos_tag(words)]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::", 1)[1] for word in words)
        return sentence

class NewlinePOSifiedText(POSifiedText):
    def sentence_split(self, text):
        return text.split("\n")


class Model:
    def __init__(self, markov_model):
        self.m = markov_model

    def dump(self, writer):
        d = {
            "version": DUMP_FMT_VERSION,
            "chain": dict(self.m.chain.model),
        }
        return json.dump(d, writer)

    @classmethod
    def load(cls, reader):
        d = json.load(reader)
        assert d["version"] == DUMP_FMT_VERSION
        # .from_json also works on dicts
        chain = Chain.from_json(d["chain"])
        return cls(POSifiedText("", chain=chain))


class ModelBuilder:
    def __init__(self, path):
        self._load(path)

    def _load(self, path):
        if path is not None and os.path.isfile(path):
            with open(path) as f:
                self._markov = Model.load(f).m
        else:
            self._markov = None

    def feed_corpus(self, text, newlines=True):
        """
        Feed a text corpus to the builder. If ``newlines`` is true (the
        default) then each line is assumed to be a sentence. We use this for
        tweets as they rarely have full sentences in them.

        It's more efficient to feed one big corpus than multiple small ones
        """
        cls = NewlinePOSifiedText if newlines else POSifiedText
        model = cls(text)

        # Avoid a call to 'combine' if this is the first corpus
        if self._markov is None:
            self._markov = model
            return

        self._markov = POSifiedText(markovify.combine([self._markov, model]))

    def model(self):
        if self._markov:
            return Model(self._markov)

    def save(self):
        with open(self.path, "w") as f:
            self.model().dump(f)
