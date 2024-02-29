import calendar
import os
import re
import textwrap
import time
import feedparser
import tweepy
from dotenv import load_dotenv
from atproto import Client, client_utils
from html2text import html2text

load_dotenv()
RSS_URLS = os.environ["RSS_URLS"].split(',')
PLATFORMS = os.environ["PLATFORMS"].split(',')
BSKY_USER = os.environ["BSKY_USER"]
BSKY_PASSWORD = os.environ["BSKY_PASSWORD"]
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
BEARER_TOKEN = os.environ["BEARER_TOKEN"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]


def truncate_too_long_text(text, width):
    return textwrap.shorten(
        text, width, placeholder="...")


def format_rss_to_text(entry, character_limit):
    text_from_html = html2text(entry.summary)

    if hasattr(entry, 'media_content'):
        if len(entry.media_content) < 1:
            text_from_html += " " + entry.media_content[0]["url"]

    if len(text_from_html) > character_limit:
        return truncate_too_long_text(text_from_html, character_limit)

    else:
        return text_from_html


def post_to_bluesky(entry):
    content = format_rss_to_text(entry, 300, 28)
    # TODO: link to original post when too long
    # tb = client_utils.TextBuilder()
    # tb.link(content[1], f'https://{content[1]}')
    # tb.text(content[0])
    bsky_client.send_post(content)


def post_to_mastodon():
    return


def post_to_twitter(entry):
    content = format_rss_to_text(entry, 280, 23)
    print(content)
    print(len(content))
    twitter_client.create_tweet(text=content)


if __name__ == "__main__":
    start_time = int(time.time())
    print("Started at", start_time)
    old_entries = []
    twitter_client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    print("Logged in to Twitter.")
    bsky_client = Client(base_url='https://bsky.social')
    bsky_client.login(os.environ['BSKY_USER'], os.environ['BSKY_PASSWORD'])
    print("Logged in to Bluesky.")

    while True:
        for rss_url in RSS_URLS:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if entry.id in old_entries:
                    pass
                elif (calendar.timegm(feed.entries[0].published_parsed) < start_time):
                    old_entries.append(entry.id)
                else:
                    if 'bluesky' in PLATFORMS:
                        post_to_bluesky(entry)
                    if 'twitter' in PLATFORMS:
                        post_to_twitter(entry)
                    old_entries.append(entry.id)
        time.sleep(10)
