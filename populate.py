# -*- coding: UTF-8 -*-

import argparse
from collections import deque
from random import sample

from blabbr.config import Config
from blabbr.twitter import TwitterConnection, tweet_text, parse_text

tc = TwitterConnection()

def safe_sample(coll, n):
    if len(coll) < n:
        return coll

    return sample(coll, n)

def write_timeline(account, f):
    for st in tc.dig(account, n=1000):
        txt = tweet_text(st)
        if not txt:
            continue
        f.write(txt)
        f.write("\n")

def main(opts):
    seed_accounts = Config().seeds()["screen_names"].strip().split("\n")[1:]

    # re-process existing texts
    with open("texts.txt") as f:
        texts = set()

        for line in f:
            txt = parse_text(line.strip())
            if not txt:
                continue

            texts.add(txt)

    texts = sorted(texts)  # set

    with open("texts.txt", "w") as f:
        for txt in texts:
            f.write(txt)
            f.write("\n")

    if opts.local:
        return

    with open("texts.txt", "a") as f:
        seen = set()
        q = deque(seed_accounts)

        try:
            while q:
                account = q.popleft()
                if account in seen:
                    continue

                print("Getting %s's timeline..." % account)
                seen.add(account)

                write_timeline(account, f)
                for friend in safe_sample(list(tc.friends(account, n=20)), 5):
                    if friend.lang != 'fr':
                        continue
                    q.append(friend.screen_name)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    main(parser.parse_args())
