# Blabbr

`blabbr` is a bot that tweets randomly-generated texts using
[Markov chains](markovify).

[markovify]: https://github.com/jsvine/markovify

## Setup

    pip install blabbr

Then follow the interactive setup:

    blabbr setup

You can also initialize a configuration file with `blabbr config init` then
fill it by hand. Check the _Config_ section below for more info.

## Run

Running a bot with `blabbr` is done in two steps: first, feed the model. Then,
use that model to generate tweets.

You can feed your model either from Twitter using a few users as a seed or from
a file that contains one tweet per line:

    # feed from Twitter
    $ blabbr populate

    # feed from a file
    $ blabbr populate --from-raw mytweets.txt

You can also retrieve tweets in a file instead of feeding them directly to the
model. This is useful in combination with `--from-raw` to check the tweets
before feeding them:

    # append tweets to tweets.txt, one per line
    $ blabbr populate --raw tweets.txt

By default the model is stored in `blabbr.json` in the current directory. You
can change that by using the `--model` option:

    $ blabbr --model mymodel.json populate

Populating an existing model doesn’t erase its previous content.

---

Once you’re happy with your model run it:

    blabbr run

The default bot follows a few rules to behave well with its human friends:

* It doesn’t tweet during the night
* It tweets less during work hours
* It never tweets more than twice in a couple of minutes

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

A few more variables can be set:

* `bot.screen_name`: Your bot's screen name. It’ll be automatically set if you
  use `blabbr setup`. This is used to save an API call when the bot needs to
  know its own name, in order to e.g. filter out its own tweets from its home
  timeline.

You can print your configuration with `blabbr config`. Use `--cfg` to specify
another path:

    $ blabbr --cfg ~/.config/blabbr.cfg <command> [options...]

Check your authentication configuration with `blabbr setup --check`.
