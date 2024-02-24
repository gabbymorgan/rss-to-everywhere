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
RSS_URL = os.environ["RSS_URL"]
BSKY_USER = os.environ["BSKY_USER"]
BSKY_PASSWORD = os.environ["BSKY_PASSWORD"]
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
BEARER_TOKEN = os.environ["BEARER_TOKEN"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]


def format_rss_to_text(entry, character_limit, hyperlink_max_length):
    html_without_a_tags = re.sub(
        r'<a href=\"(.*?)\".*/a>', r'\1', entry.summary)
    text_from_html = html2text(html_without_a_tags)[:-2]

    if hasattr(entry, 'media_content'):
        media_url = entry.media_content[0]["url"]
        too_long_with_media_url = len(
            text_from_html) + min(len(media_url), hyperlink_max_length) > character_limit
        if (len(entry.media_content) > 2 or too_long_with_media_url):
            summary = textwrap.shorten(
                text_from_html, width=character_limit - hyperlink_max_length, placeholder="...")
            return f'{summary}{entry.link}'
        else:
            return f'{text_from_html}{media_url}'
    elif len(text_from_html) > character_limit:
        summary = textwrap.shorten(
            text_from_html, width=character_limit - hyperlink_max_length, placeholder="...")
        return f'{text_from_html} {entry.link}'
    else:
        return text_from_html


def post_to_bluesky(entry):
    tb = client_utils.TextBuilder()
    content = format_rss_to_text(entry, 300, 28)
    content_with_link = content.split("https://")
    if len(content_with_link) == 2:
        tb.text(content_with_link[0])
        tb.link(content_with_link[1], f'https://{content_with_link[1]}')
        bsky_client.send_post(tb)
    else:
        bsky_client.send_post(content)
    return


def post_to_mastodon():
    return


def post_to_twitter(entry):
    content = format_rss_to_text(entry, 280, 23)
    twitter_client.create_tweet(text=content)
    return


if __name__ == "__main__":
    start_time = int(time.time())
    url = os.environ["RSS_URL"]
    old_entries = []
    twitter_client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    bsky_client = Client(base_url='https://bsky.social')
    bsky_client.login(os.environ['BSKY_USER'], os.environ['BSKY_PASSWORD'])
    while True:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.id in old_entries:
                pass
            elif (calendar.timegm(feed.entries[0].published_parsed) < start_time):
                old_entries.append(entry.id)
            else:
                post_to_bluesky(entry)
                post_to_twitter(entry)
                old_entries.append(entry.id)
        time.sleep(300)
