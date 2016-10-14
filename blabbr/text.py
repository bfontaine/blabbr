# -*- coding: UTF-8 -*-

import re

def parse_text(text):
    """
    Parse a source tweet text. Return ``None`` if it shouldn't be used.
    """

    text = re.sub(r"https?://[^ ]*", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    if not text:
        return

    ltext = text.lower()
    for prefix in ("rt ", "mt ", "@", ".@", "je ", "moi ", "mon ", "ma ", "mes "):
        if ltext.startswith(prefix):
            return

    # truncated
    if text.endswith("…"):
        return

    # quick normalization
    repls = (
        (r"&gt;", ">"),
        (r"&lt;", "<"),
        (r"&amp;", "&"),

        # "pr Person" -> "pour Person"
        (r"\bpr\b", "pour"),
        # "foo:" -> "foo :"
        (r"\b:", " :"),
        # ".!!!" -> "!"
        (r"\.+!+", "!"),
        # ".?!!!" -> "?!"
        (r"\.+\?+!+", "!"),
        # "foo!!" -> "foo !"
        (r"\b!_", " !"),
        # "25 %" -> "25%"
        (r"\b %", "%"),
        (r" \.", "."),

        (r"\b\.\.\b", "... "),

        # "[...]" -> "..."
        (r"\[\.\.\.+\]", "..."),

        (r"\.+…\.*", "…"),

        # "foo bar :" -> "foo bar"
        (r":$", ""),

        # "aa|bb" -> "aabb"
        (r"\|", ""),

        (r"via @[^ ]+$", ""),

        (r"\bgvt\b", "gouvernement"),

        (r"(?:via )?#feedly", ""),
        (r"via$", ""),

        (r"-$", ""),
    )

    for before, after in repls:
        text = re.sub(before, after, text).strip()

    # join spaces
    text = re.sub(r"\s+", " ", text)

    if re.match(r"^\w+ :", text):
        # Those are mostly headlines
        return

    return text
