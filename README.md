# Blabbr

`blabbr` is a bot that tweets randomly-generated texts using
[Markov chains](markovify).

[markovify]: https://github.com/jsvine/markovify

## Setup

    pip install blabbr

Then follow the interactive setup:

    blabbr setup

You can also initialize a configuration file with `blabbr config init` then
fill it by hand.

## Run

Running a bot with `blabbr` is done in two steps: first, feed the model. Then,
use that model to generate tweets.

    blabbr run

### Config

A bot needs a configuration file to run. By default it tries to find
`blabbr.cfg` in the current directory and fallback on `~/.blabbr.cfg`. You can
give a custom path with `--cfg <path>`.

The default config file looks like this:

```ini
[seeds]
screen_names = 

[auth]
token = 
consumer_secret = 
consumer_key = 
token_secret = 

[bot]
timezone = Europe/Paris
unfollow = True
retweet = True
lang = en
like = True
follow = True
```

* `seeds.screen_names` should be a comma-separated list of Twitter usernames.
  Those are used as seeds to retrieve tweets. By default it fetches their last
  1000 tweets then check 10 of the users they follow and so on. See
  `blabbr populate --help` for more info on how to change that behavior.
* `auth.token` and similar keys are needed for the Twitter API. Run
   `blabbr setup --help` for more info.
* `bot.timezone` is the bot’s timezone. This is important so that it doesn’t
  tweet in the middle of the night.
* `bot.lang` is used to filter tweets when populating the model.
* `bot.follow` and other boolean options are flags to enable/disable some of
  the bot's actions. Right now only the `tweet` feature is implemented.
