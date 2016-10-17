# -*- coding: UTF-8 -*-

import time
from random import randint, random
from datetime import timedelta

from blabbr.generation import Generator
from blabbr.twitter import TwitterClient
from blabbr.logging import getLogger

from blabbr.time import Clock

MIN_TWEET_INTERVAL = timedelta(minutes=20)


class Bot:
    """
    A Twitter bot.
    """

    def __init__(self, cfg=None, generator=None, clock=None, model=None,
                 dry_run=False, debug=False):
        self.twitter = TwitterClient(cfg=cfg)
        self.clock = Clock(cfg) if clock is None else clock
        self.logger = getLogger("bot")

        if generator:
            self.generator = generator
        elif model:
            self.generator = Generator(model)
        else:
            raise RuntimeError("The bot needs a generator or a model")

        if debug:
            dry_run = True

        self.features = cfg.enabled_features()
        self.dry_run = dry_run
        self.debug = debug
        self.last_tweet = None
        self.last_tweet_time = None

    def live(self):
        """
        Start the bot's life. This methods never returns but may raise
        exceptions.
        """
        self.logger.debug("Starting to live...")
        self.logger.debug("Dry run: %s" % self.dry_run)

        while True:
            if self.clock.time_to_sleep():
                self.logger.debug("Sleeping...")
                self.sleep(40, 50)
                continue

            if not self.clock.time_to_chill():
                self.logger.debug("Not a time to chill...")
                self.sleep(20, 25)
                continue

            self.tick()
            self.sleep(1, 2)

    def tick(self):
        """
        This method is called every one to two minutes when the bot has free
        time.
        """
        self.logger.debug("tick")
        feeling_inspired = random() > 0.7
        if not feeling_inspired:
            self.logger.debug("Not feeling inspired")
            return

        self.tweet()

    def tweet(self):
        """
        Post a random tweet. This has no effect if the last tweet was less than
        20s ago or if the ``tweet`` feature is disabled.
        """
        if not self.features.get("tweet", True):
            self.logger.debug("Tweeting is disabled in the config")
            return

        now = self.clock.now()
        if self.last_tweet_time and \
                now < self.last_tweet_time + MIN_TWEET_INTERVAL:
            return

        text = self.generator.tweet()
        self.logger.debug("About to tweet: %s" % text)
        if not self.dry_run:
            self.twitter.tweet(text)

        self.last_tweet = text
        self.last_tweet_time = now

    def sleep(self, minutes_min, minutes_max):
        """
        Sleep a random time between the given number of minutes.
        """
        duration = randint(minutes_min * 60, minutes_max * 60)
        if self.debug:
            self.logger.debug("Would sleep %d seconds" % duration)
        else:
            time.sleep(duration)


if __name__ == "__main__":
    Bot().live()
