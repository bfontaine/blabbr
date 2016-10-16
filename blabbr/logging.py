# -*- coding: UTF-8 -*-

import logging

def getLogger(name):
    logger = logging.getLogger("blabbr.%s" % name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

        logger.addHandler(ch)

    return logger
