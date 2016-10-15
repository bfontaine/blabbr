# -*- coding: UTF-8 -*-

import time
from random import randint, random
from datetime import timedelta

from blabbr.generation import Generator
from blabbr.twitter import TwitterClient

from blabbr.time import Clock

MIN_TWEET_INTERVAL = timedelta(minutes=20)

class Bot:
    def __init__(self, cfg=None, generator=None, clock=None, model=None):
        self.twitter = TwitterClient(cfg=cfg)
        self.clock = Clock() if clock is None else clock

        if generator:
            self.generator = generator
        elif model:
            self.generator = Generator(model)
        else:
            self.generator = Generator()

        self.last_tweet = None
        self.last_tweet_time = None

    def live(self):
        """
        Start the bot's life
        """
        while True:
            if self.schedule.time_to_sleep():
                self.sleep(40, 50)
                continue

            if not self.schedule.time_to_chill():
                self.sleep(20, 25)
                continue

            self.tick()
            self.sleep(1, 2)

    def tick(self):
        """
        This method is called every one to two minutes when the bot has free
        time.
        """
        feeling_inspired = random() > 0.7
        if not feeling_inspired:
            return

        self.tweet()

    def tweet(self):
        """
        Post a random tweet. This has no effect if the last tweet was less than
        20s ago.
        """
        if self._last_tweet_time and \
                self.schedule.now() < self._last_tweet_time + MIN_TWEET_INTERVAL:
            return

        text = self.generator.tweet()
        self.twitter.tweet(text)

        self._last_tweet = text
        self._last_tweet_time = self.schedule.now()

    def sleep(self, minutes_min, minutes_max):
        """
        Sleep a random time between the given number of minutes.
        """
        time.sleep(randint(minutes_min * 60, minutes_max * 60))


if __name__ == "__main__":
    Bot().live()
