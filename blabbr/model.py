# -*- coding: UTF-8 -*-

import re
import nltk
import markovify
import markovify.text

from markovify.chain import Chain


# Simple format versionning
# Version 1: %blabbr<version>\n<chain json>
DUMP_FMT_VERSION = 1

# from https://github.com/jsvine/markovify#extending-markovifytext
class POSifiedText(markovify.NewlineText):
    def word_split(self, sentence):
        words = re.split(self.word_split_pattern, sentence)
        words = ["::".join(tag) for tag in nltk.pos_tag(words)]
        return words

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


class Model:
    def __init__(self, markov_model_or_source_text):
        if isinstance(markov_model_or_source_text, markovify.text.Text):
            self.m = markov_model_or_source_text
        else:
            self.m = POSifiedText(markov_model_or_source_text)

    def dump(self, writer):
        m = self.m.chain.to_json()
        writer.write("%%blabbr%d\n%s" % (DUMP_FMT_VERSION, m))

    @classmethod
    def load(cls, reader):
        expected_header = "%%blabbr%d\n" % DUMP_FMT_VERSION
        header = reader.read(len(expected_header))
        assert header == expected_header
        chain = Chain.from_json(reader.read())
        return cls(POSifiedText("", chain=chain))
