# -*- coding: UTF-8 -*-

import time
import logging
import random
import arrow
from datetime import timedelta

from blabbr.generation import Generator
from blabbr.twitter import TwitterConnection

logging.basicConfig(level=logging.DEBUG)

def now():
    return arrow.utcnow().to("Europe/Paris")

class Bot:
    def __init__(self):
        self.twitter = TwitterConnection()
        self.generator = Generator()
        self._last_tweet = now()

    def live(self):
        try:
            logging.info("Starting to live...")
            self._live()
        except KeyboardInterrupt:
            pass

    def tweet(self):
        if now() < self._last_tweet + timedelta(seconds=20):
            logging.warning("I refuse to tweet more than twice in 20s")
            return

        text = self.generator.tweet()
        logging.info("About to tweet: %s" % text)
        self.twitter.tweet(text)
        self._last_tweet = now()

    def _live(self):
        while True:
            time.sleep(random.random() * 10)
            self._tick()

    def _tick(self):
        tm = now().time()
        day_ts = tm.hour * 3600 + tm.minute * 60 + tm.second

        sleeping_time = random.randint(
            22 * 3600,
            24 * 3600 - 1,
        )

        if day_ts > sleeping_time:
            logging.info("Time to go to bed")
            time.sleep(8 * 3600)
            return

        wakeup_time = random.randint(
            9 * 3600,
            11 * 3600,
        )
        if day_ts < wakeup_time:
            logging.info("I'd prefer not wake up now")
            time.sleep(3600)
            return

        time_to_chill = random.random() > 0.6
        if not time_to_chill:
            logging.info("Not a time to chill")
            time.sleep(random.random() * 3600 + 1800)
            return

        burst = random.random() >= 0.9
        if not burst:
            self.tweet()
            time.sleep(random.random() * 2 * 120 + 20)
            return

        logging.info("I'm feeling a burst of inspiration")
        n = int(random.random() * 5 + 1)
        for _ in range(n):
            self.tweet()
            time.sleep(random.random() * 60 + 20)


if __name__ == "__main__":
    Bot().live()
