# -*- coding: UTF-8 -*-

import sys
import os.path
import textwrap

import click
import tweepy

from blabbr.config import Config

class Cli:
    DEFAULT_CONFIG_PATH = "~/.blabbr.cfg"

    def __init__(self, cfg, **kw):
        self.cfg = Config(os.path.expanduser(cfg))

    def print_text(self, text, width=80, **kw):
        text = textwrap.dedent(text).strip()

        paragraphs = [
            textwrap.fill(p, width=width)
            for p in text.split("\n\n")]

        click.echo("\n\n".join(paragraphs), **kw)

    def setup(self, **kw):
        self.setup_auth(**kw)
        self.setup_nltk(**kw)

    def setup_auth(self, noninteractive=False, force=False, **kw):
        if not force and self.cfg.get_auth():
            click.echo("The bot is already setup! Use --force if you're sure.",
                        err=True)
            sys.exit(1)

        auth = {k: kw.get(k) for k in \
                ("consumer_key", "consumer_secret", "token", "token_secret")}

        missing_infos = set(k for k, v in auth.items() if v is None)

        if missing_infos:
            if noninteractive:
                click.echo("Missing auth info: %s" % ", ".join(missing_infos),
                            err=True)
                sys.exit(1)

            if missing_infos & {"consumer_key", "consumer_secret"}:
                self.print_text("""
                    You need to create a Twitter app in order to access the
                    Twitter API. Go on the following page:

                        https://apps.twitter.com/app/new

                    You don't have to fill the callback URL. Also, the account
                    with which you create your app has little importance as
                    long as you have a valid mobile phone number attached to
                    it.

                    Once you're done, go on the "Keys and Access Tokens" tab
                    and copy the consumer key & secret here.
                """)
                click.echo()

                auth["consumer_key"] = input("Consumer key: ").strip()
                auth["consumer_secret"] = input("Consumer secret: ").strip()
                click.echo()

            if missing_infos & {"token", "token_secret"}:
                oauth = tweepy.OAuthHandler(auth["consumer_key"],
                                            auth["consumer_secret"])
                redirect_url = oauth.get_authorization_url()

                self.print_text("""
                    You need to create an account for your bot then make it
                    allow your app to use its account.

                    Open this URL in a browser in which you're logged with your
                    bot's account. It'll give you a verification code you'll
                    copy back here.
                """)

                click.echo("\n    %s\n" % redirect_url)

                code = input("Verification code: ")
                oauth.get_access_token(code)
                auth["token"] = oauth.access_token
                auth["token_secret"] = oauth.access_token_secret
                click.echo()

        click.echo("Your bot is set up!")

        self.cfg.set_auth(auth)
        self.cfg.save()

    def setup_nltk(self, **kw):
        import nltk
        from nltk.data import find

        tagger = "averaged_perceptron_tagger"

        try:
            find("taggers/%s" % tagger)
        except LookupError:
            click.echo("Downloading NTLK data (~2MB)...")
            nltk.download(tagger)

    def populate(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()


@click.group()
@click.option('--cfg', default=Cli.DEFAULT_CONFIG_PATH,
              type=click.Path(),
              help="Path to the config")
@click.pass_context
def cli(ctx, cfg):
    ctx.obj = Cli(cfg=cfg)

@cli.command()
@click.option("--consumer-key", metavar="KEY", help="Consumer key (API key)")
@click.option("--consumer-secret", metavar="SECRET",
              help="Consumer secret (API secret)")
@click.option("--token", metavar="TOKEN", help="Access token")
@click.option("--token-secret", metavar="SECRET", help="Access token secret")
@click.option("--noninteractive", is_flag=True,
              help=(
                  "Fail if one option is missing instead of offering an"
                  " interactive setup."))
@click.option("--force", is_flag=True,
              help="Force the setup even if the bot is already set.")
@click.pass_obj
def setup(cli, *args, **kw):
    """Setup the bot's config"""
    cli.setup(*args, **kw)

@cli.command()
@click.pass_obj
def populate(cli, *args, **kw):
    """Populate the text corpus"""
    cli.populate(*args, **kw)

@cli.command()
@click.pass_obj
def run(cli, *args, **kw):
    """Run the bot"""
    cli.run(*args, **kw)

if __name__ == "__main__":
    cli()
