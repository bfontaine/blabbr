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

        # Lower-case what we're pretty sure are not accronyms
        (r"([A-Z]{6,})", lambda m: m.group(1).lower()),

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

        (r" :: ", " "),
        (r" :- ", " "),

        (r"\b\.\.\b", "... "),

        # "[...]" -> "..."
        (r"\[\.\.\.+\]", "..."),
        # ":..." -> "..."
        (r":\.\.\.+", "..."),

        # Fix bogus ellipsis e.g. "...…" -> "…"
        (r"\.+…\.*", "…"),

        # Remove ':' or '-' at the end of the tweet
        (r"[-:@]$", ""),

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

def fix_punctuation(text):
    # This may vary per language
    text = text.replace(" ' ", "'")
    text = re.sub(" ([\.,])", "\\1", text)

    return text
