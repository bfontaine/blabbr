# -*- coding: UTF-8 -*-

from random import randint, random

import arrow


class Clock:
    """
    A clock to be used by a ``Bot``.
    """

    def __init__(self, cfg):
        self.tz = cfg.get("bot", "timezone")

    def time_to_sleep(self):
        """
        Return True if it's time to sleep.
        """
        h, m = self.clock()
        day_ts = h * 60 + m

        # Sleep at some point between 22:00 and 23:59
        sleeping_time = randint(22 * 60, 24 * 60 - 1)
        # Wake up at some point between 9:00 and 11:00
        wakeup_time = randint(9 * 60, 11 * 60)

        return day_ts > sleeping_time or day_ts < wakeup_time

    def weekend(self):
        """
        Return ``True`` if it's the weekend.
        """
        # Monday = 0
        # ...
        # Saturday = 5
        # Sunday = 6
        return self.now().weekday() in (5, 6)

    def time_to_chill(self):
        """
        Return ``True`` if the bot currently have some time to chill; i.e. it's
        free to tweet.
        """
        h, _ = self.clock()

        # Our bot has less time to chill during work hours
        if not self.weekend() and (10 <= h <= 11 or 14 <= h <= 17):
            return random() > 0.7

        return random() > 0.5

    def now(self):
        """
        Return the current time.
        """
        return arrow.utcnow().to(self.tz)

    def clock(self):
        """
        Return a tuple of ``(hours, minutes)`` that represent the time in the
        bot's timezone.
        """
        tm = self.now().time()
        return tm.hour, tm.minute
