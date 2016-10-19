# -*- coding: UTF-8 -*-

import re

# From:
#   http://stackoverflow.com/a/33417311/735926
#   http://jrgraphix.net/r/Unicode/2600-26FF
#   https://en.wikipedia.org/wiki/Enclosed_Alphanumeric_Supplement
#   https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation
#   https://en.wikipedia.org/wiki/Miscellaneous_Technical
#   https://en.wikipedia.org/wiki/Variation_Selectors_(Unicode_block)
EMOJI_RE = re.compile("["
    "\U00002300-\U000023FF"  # misc technical symbols
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U00003000-\U0000303F"  # CJK symbols (Chinese/Japanese/Korean)
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0001F100-\U0001F1FF"  # enclosed chars
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "]+")

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

        (EMOJI_RE, ""),

        # Treat quotes as parts of the tweet for more fun
        (r'["“”«»]', " "),

        # Remove random punctuation at the beginning & the end
        (r"^[-'&/\.,;><=]+", ""),
        (r"[-/><=:@&]+$", ""),

        # Lower-case what we're pretty sure are not accronyms
        (r"([A-ZÀÈÌÒÙÁÉÍÓÚÝÂÊÎÔÛÄËÏÖÜŸ]{6,})", lambda m: m.group(1).lower()),

        # "foo:" -> "foo :" (FR)
        (r"\b:", " :"),
        # "foo?" -> "foo ?" (FR)
        (r"\b\?", " ?"),
        # ".!!!" -> "!"
        (r"\.*!+\.*", "!"),
        # ".?!!!" -> "?!"
        (r"\.*\?+!+\.*", "?!"),
        # "foo!!" -> "foo !" (FR)
        (r"\b!+", " !"),
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
        (r"\.*…\.*", "… "),

        # Remove "via @foo"
        (r"via @[^ ]+$", ""),
        (r"(?:via )?#feedly", ""),
        (r"via$", ""),

        # "aa | bb" -> "aa  bb"
        (r"\|", ""),
    )

    for before, after in repls:
        text = re.sub(before, after, text).strip()

    typos = (
        # FR abbreviations & typos
        (r"\bpr\b", "pour"),
        (r"\bc est ", "c'est "),
        (r"\bs'est ", "c'est "),
    )

    for before, after in typos:
        text = re.sub(before, after, text, flags=re.IGNORECASE).strip()

    return merge_spaces(text)


def fix_punctuation(text):
    # This may vary per language
    text = re.sub(r" (['’]) ", "\\1", text)
    text = re.sub(r" ([\.,])", "\\1", text)

    return text
