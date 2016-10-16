# -*- coding: UTF-8 -*-

import sys
import time

import tweepy
import tweepy.auth


class TwitterClient:
    @classmethod
    def __init__(self, cfg):
        ks = cfg.get_auth()

        auth = tweepy.OAuthHandler(ks["consumer_key"],
                                   ks["consumer_secret"])
        auth.set_access_token(ks["token"], ks["token_secret"])
        self.api = tweepy.API(auth)

    def user_tweets(self, user_id, n=20):
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
            print("Sleeping...", file=sys.stderr)
            time.sleep(sleeping_time)
