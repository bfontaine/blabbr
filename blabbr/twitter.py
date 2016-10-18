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

    def verify_credentials(self):
        return self.api.verify_credentials()

    def user_tweets(self, user_id, n=20):
        return rate_limited_generator(self.api.user_timeline, n, id=user_id)

    def home_tweets(self, n=20):
        """
        Return up to ``n`` tweets from the bot's timeline.
        """
        return rate_limited_generator(self.api.home_timeline, n)

    def tweet(self, text):
        self.api.update_status(text)

    def friends(self, user_id, n=20):
        return rate_limited_generator(self.api.friends, n, id=user_id)


def rate_limited(cursor, sleeping_time=(15*60+5)):
    while True:
        try:
            yield next(cursor)
        except tweepy.RateLimitError:
            print("Sleeping...", file=sys.stderr)
            time.sleep(sleeping_time)

def rate_limited_generator(method, n, **kw):
    cursor = tweepy.Cursor(method, count=n, **kw)
    for el in rate_limited(cursor.items(n)):
        yield el
