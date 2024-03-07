import calendar
import os
import requests
import time
import feedparser
import tweepy
import nltk.data
from dotenv import load_dotenv
from atproto import Client, client_utils
from html2text import html2text

load_dotenv()
RSS_URLS = os.environ['RSS_URLS'].split(',')
PLATFORMS = os.environ['PLATFORMS'].split(',')
BSKY_USER = os.environ['BSKY_USER']
BSKY_PASSWORD = os.environ['BSKY_PASSWORD']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
BEARER_TOKEN = os.environ['BEARER_TOKEN']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
MASTODON_BASE_URL = os.environ['MASTODON_BASE_URL']
MASTODON_APP_TOKEN = os.environ['MASTODON_APP_TOKEN']


def html_to_text(htmlString):
    return html2text(htmlString)


def shorten_text(entry):
    text_from_html = html_to_text(entry.summary)
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    return sent_detector.tokenize(text_from_html)[0]


def post_to_bluesky(entry):
    content = shorten_text(entry)
    tb = client_utils.TextBuilder()
    tb.text(content)
    tb.link(entry.link, entry.link)
    bsky_client.send_post(tb)


def post_to_mastodon(entry):
    status = html_to_text(entry.summary)
    print(status)
    requests.post(f'{MASTODON_BASE_URL}/api/v1/statuses',
                  data=f'status={status}', headers={'Authorization': f'Bearer {MASTODON_APP_TOKEN}'})
    return


def post_to_twitter(entry):
    twitter_client.create_tweet(
        text=shorten_text(entry) + ' ' + entry.link)


if __name__ == '__main__':
    start_time = int(time.time())
    print('Started at', start_time)
    nltk.download('punkt')
    print('Punkt downloaded.')
    old_entries = []

    if 'bluesky' in PLATFORMS:
        bsky_client = Client(base_url='https://bsky.social')
        bsky_client.login(os.environ['BSKY_USER'], os.environ['BSKY_PASSWORD'])
        print('Logged in to Bluesky.')

    if 'twitter' in PLATFORMS:
        twitter_client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        print('Logged in to Twitter.')

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
                    if 'mastodon' in PLATFORMS:
                        post_to_mastodon(entry)
                    old_entries.append(entry.id)
        time.sleep(10)
