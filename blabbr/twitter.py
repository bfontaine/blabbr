# -*- coding: UTF-8 -*-

import re
import time

import tweepy
import tweepy.auth

from blabbr.config import Config

def oauth_dance(consumer_key, consumer_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    redirect_url = auth.get_authorization_url()
    print(redirect_url)
    code = input("Verification code: ")
    auth.get_access_token(code)
    return {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "token_key": auth.access_token,
        "token_secret": auth.access_token_secret,
    }

class TwitterConnection:
    @classmethod
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = Config()

        ks = cfg.get_auth()

        auth = tweepy.OAuthHandler(ks["consumer_key"],
                                   ks["consumer_secret"])
        auth.set_access_token(ks["token_key"], ks["token_secret"])
        self.api = tweepy.API(auth)

    def dig(self, user_id, n=20):
        cursor = tweepy.Cursor(self.api.user_timeline, id=user_id, count=n)
        for status in rate_limited(cursor.items(n)):
            yield status

    def tweet(self, text):
        self.api.update_status(text)

    def friends(self, user_id, n=20):
        cursor = tweepy.Cursor(self.api.friends, id=user_id, count=n)
        for account in rate_limited(cursor.items(n)):
            yield account


def rate_limited(cursor, sleeping_time=(15*60+5)):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            print("Sleeping...")
            time.sleep(sleeping_time)

def parse_text(text):
    text = re.sub(r"https?://[^ ]*", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    if not text:
        return

    ltext = text.lower()
    for prefix in ("rt ", "mt ", "@", ".@", "je ", "moi ", "mon ", "ma ", "mes "):
        if ltext.startswith(prefix):
            return

    # truncated
    if text.endswith("…"):
        return

    # quick normalization
    repls = (
        (r"&gt;", ">"),
        (r"&lt;", "<"),
        (r"&amp;", "&"),

        # "pr Person" -> "pour Person"
        (r"\bpr\b", "pour"),
        # "foo:" -> "foo :"
        (r"\b:", " :"),
        # ".!!!" -> "!"
        (r"\.+!+", "!"),
        # ".?!!!" -> "?!"
        (r"\.+\?+!+", "!"),
        # "foo!!" -> "foo !"
        (r"\b!_", " !"),
        # "25 %" -> "25%"
        (r"\b %", "%"),
        (r" \.", "."),

        (r"\b\.\.\b", "... "),

        # "[...]" -> "..."
        (r"\[\.\.\.+\]", "..."),

        (r"\.+…\.*", "…"),

        # "foo bar :" -> "foo bar"
        (r":$", ""),

        # "aa|bb" -> "aabb"
        (r"\|", ""),

        (r"via @[^ ]+$", ""),

        (r"\bgvt\b", "gouvernement"),

        (r"(?:via )?#feedly", ""),
        (r"via$", ""),

        (r"-$", ""),
    )

    for before, after in repls:
        text = re.sub(before, after, text).strip()

    # join spaces
    text = re.sub(r"\s+", " ", text)

    if re.match(r"^\w+ :", text):
        # Those are mostly headlines
        return

    return text

def tweet_text(t):
    if t.lang not in (None, "und", "fr"):
        return

    if t.is_quote_status:
        return

    return parse_text(t.text)
