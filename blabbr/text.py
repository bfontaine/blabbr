# -*- coding: UTF-8 -*-

import re

def merge_spaces(text):
    return re.sub(r"\s+", " ", text)

def strip_urls(text):
    """Remove (truncated) URLs"""
    return re.sub(r"https?://[^ ]*", "", text)

def normalize(text):
    repls = (
        (r"&gt;", ">"),
        (r"&lt;", "<"),
        (r"&amp;", "&"),

        # FR abbreviations
        (r"\bpr\b", "pour"),
        (r"\bgvt\b", "gouvernement"),

        # "foo:" -> "foo :" (FR)
        (r"\b:", " :"),
        # ".!!!" -> "!"
        (r"\.+!+\.*", "!"),
        # ".?!!!" -> "?!"
        (r"\.+\?+!+\.*", "!"),
        # "foo!!" -> "foo !" (FR)
        (r"\b!_", " !"),
        # "25 %" -> "25%"
        (r"\b %", "%"),
        # "blabla ." -> "blabla."
        (r" \.", "."),

        (r"\b\.\.\b", "... "),

        # "[...]" -> "..."
        (r"\[\.\.\.+\]", "..."),

        # Fix bogus ellipsis e.g. "...…" -> "…"
        (r"\.+…\.*", "…"),

        # Remove ':' or '-' at the end of the tweet
        (r"[-:]$", ""),

        # Remove "via @foo"
        (r"via @[^ ]+$", ""),
        (r"(?:via )?#feedly", ""),
        (r"via$", ""),

        # "aa | bb" -> "aa  bb"
        (r"\|", ""),
    )

    for before, after in repls:
        text = re.sub(before, after, text).strip()

    return text
