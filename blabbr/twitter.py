# -*- coding: UTF-8 -*-

import time

import tweepy
import tweepy.auth

from blabbr.config import Config
from blabbr.text import parse_text

class TwitterClient:
    @classmethod
    def __init__(self, cfg=None):
        if cfg is None:
            cfg = Config()

        ks = cfg.get_auth()

        auth = tweepy.OAuthHandler(ks["consumer_key"],
                                   ks["consumer_secret"])
        auth.set_access_token(ks["token"], ks["token_secret"])
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

def tweet_text(t):
    if t.lang not in (None, "und", "fr"):
        return

    if t.is_quote_status:
        return

    return parse_text(t.text)
