# -*- coding: UTF-8 -*-

import re
import json
import os.path
from collections import deque

import nltk
from nltk.tokenize import TweetTokenizer
import markovify
import markovify.text
from markovify.chain import Chain

from blabbr.twitter import TwitterClient
from blabbr.logging import getLogger
from blabbr import text as tx

# Simple format versionning
DUMP_FMT_VERSION = 1


# from https://github.com/jsvine/markovify#extending-markovifytext
class POSifiedText(markovify.Text):
    def __init__(self, input_text, state_size=2, chain=None):
        self.tokenizer = TweetTokenizer(reduce_len=True)

        self.tag_sep = "@::@"

        # Circumvent some limitations of markovify by allowing one to create a
        # POSifiedText from a markovify.Text instance
        if isinstance(input_text, markovify.Text):
            m = input_text
            self.input_text = m.input_text
            self.rejoined_text = m.rejoined_text
            self.chain = m.chain
        else:
            super().__init__(input_text, state_size, chain)

    def word_split(self, sentence):
        words = self.tokenizer.tokenize(sentence)
        words = [self.tag_sep.join((tag, word))
                 for word, tag in nltk.pos_tag(words) if word]
        return words

    def word_join(self, words):
        return " ".join(word.split(self.tag_sep, 1)[1] for word in words)


class NewlinePOSifiedText(POSifiedText):
    def sentence_split(self, text):
        return text.split("\n")


class Model:
    def __init__(self, markov_model):
        self.m = markov_model

    def make_tweet(self, size=140, tries=100, max_overlap_ratio=0.5, **kw):
        return self.m.make_short_sentence(size, tries=tries,
                                          max_overlap_ratio=max_overlap_ratio,
                                          **kw)

    def dump(self, writer):
        d = {
            "version": DUMP_FMT_VERSION,
            # We can't store a dict because JSON doesn't accept lists as keys
            "chain": list(self.m.chain.model.items()),
        }
        return json.dump(d, writer)

    @classmethod
    def load(cls, reader):
        d = json.load(reader)
        assert d["version"] == DUMP_FMT_VERSION
        items = [(tuple(k), v) for k, v in d["chain"]]

        # .from_json also works on dicts
        chain = Chain.from_json(dict(items))
        return cls(NewlinePOSifiedText("", chain=chain))


class ModelBuilder:
    def __init__(self, path):
        self.path = path
        self._load()

    def _load(self):
        if self.path is not None and os.path.isfile(self.path):
            with open(self.path) as f:
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

        self._markov = cls(markovify.combine([self._markov, model]))

    def model(self):
        if self._markov:
            return Model(self._markov)

    def save(self):
        model = self.model()
        if not model:
            return

        with open(self.path, "w") as f:
            model.dump(f)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()


class TwitterDigger:
    def __init__(self, cfg):
        names = cfg.get("seeds", "screen_names")
        self.names = deque([n.strip() for n in names.split(",")])
        self._seen = set()
        self._twitter = TwitterClient(cfg)
        self._lang = cfg.get("bot", "lang")
        self.logger = getLogger("digger")

    def screen_names(self, pick_friends=10):
        """
        Generate Twitter screen names from the configured seed list
        """
        while self.names:
            screen_name = self.names.popleft()
            if screen_name in self._seen:
                continue
            self._seen.add(screen_name)
            yield screen_name

            if pick_friends <= 0:
                continue

            for friend in self._twitter.friends(screen_name, n=pick_friends):
                if self._lang and friend.lang != self._lang:
                    continue
                if friend.protected or not friend.statuses_count:
                    continue
                self.names.append(friend.screen_name)

    def account_timeline(self, screen_name, size=1000):
        """
        Yield an account's last tweets. Tweets are filtered and cleaned up so
        the returned size might be lower than the one given as an argument
        (default is 1000).
        """
        acceptable_languages = set()
        if self._lang:
            # Accept tweets with unknown languages
            acceptable_languages = set((None, "und", self._lang))

        for status in self._twitter.user_tweets(screen_name, n=size):
            text = filter_status(status, acceptable_languages)
            if text:
                yield text

    def tweets(self, pick_friends=10, timeline_size=1000):
        """
        Generate tweets from seed accounts' timelines and their friends'.
        """
        self.logger.debug((
            "Retrieving tweets with options pick_friends=%d,"
            " timeline_size=%d") % (pick_friends, timeline_size))

        for name in self.screen_names(pick_friends=pick_friends):
            self.logger.debug("Checking @%s..." % name)
            for text in self.account_timeline(name, size=timeline_size):
                yield text

def filter_status(status, languages=None):
    if languages and status.lang not in languages:
        return

    if status.is_quote_status:
        return

    return filter_status_text(status.text)

def filter_status_text(text):
    text = tx.merge_spaces(text)
    text = tx.strip_urls(text)

    min_length = 30  # Arbitrary

    text = text.strip()
    # Don't yield empty or too short texts
    if len(text) < min_length:
        return

    lower_text = text.lower()
    for prefix in (
            # Global
            "rt ", "mt ", "@", ".@",
            # FR
            "je ", "moi ", "mon ", "ma ", "mes ",
            # EN
            "i ", "my "):
        if lower_text.startswith(prefix):
            return

    # truncated
    if text.endswith("…"):
        return

    # Those are mostly headlines
    if re.match(r"^[-\w]+ *:", text):
        return

    text = tx.normalize(text)

    # Re-check the text length now that it has been normalized
    if len(text) < min_length:
        return

    # Remove tweets that consist of hashtags/mentions only
    if [w for w in text.split(" ") if w.startswith("#") or w.startswith("@")]:
        return

    # Remove tweets with no text
    if re.match(r"^\W+$", text):
        return

    return text
