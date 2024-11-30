import calendar
import os
import requests
import time
import feedparser
from dotenv import load_dotenv
from atproto import Client, client_utils

load_dotenv()
BSKY_USER = os.environ['BSKY_USER']
BSKY_PASSWORD = os.environ['BSKY_PASSWORD']
MASTODON_BASE_URL = os.environ['MASTODON_BASE_URL']
MASTODON_APP_TOKEN = os.environ['MASTODON_APP_TOKEN']
RSS_URLS = os.environ['RSS_URLS'].split(',')
PLATFORMS = os.environ['PLATFORMS'].split(',')
REFRESH_INTERVAL = int(os.environ['REFRESH_INTERVAL'])

def size_description_to_fit(entry, char_limit, max_url_length, url_shortened=False):
    url_length = len(entry.link)
    title_length = len(entry.title)
    if url_shortened == True:
        url_length = min(url_length, max_url_length)
    max_description_length = char_limit - url_length - title_length - 7

    print(url_length, title_length, max_description_length)

    return f'{entry.title}\n----\n{entry.description[:max_description_length]}\n{entry.link} '

def post_to_bluesky(entry):
    status = f'{entry.title}\n{entry.description}'
    tb = client_utils.TextBuilder()
    tb.text(status)
    tb.link(entry.link, entry.link)
    bsky_client.send_post(tb)


def post_to_mastodon(entry):
    status = size_description_to_fit(entry, 500, 500)
    r = requests.post(f'{MASTODON_BASE_URL}/api/v1/statuses',
                  data=f'status={status}', headers={'Authorization': f'Bearer {MASTODON_APP_TOKEN}'})
    print(r.text)


def post_to_console(entry):
    print(f'{entry.title}\n{entry.description}\n{entry.link}')


if __name__ == '__main__':
    start_time = int(time.time())
    print('Started at', start_time)
    old_entries = []

    if 'bluesky' in PLATFORMS:
        bsky_client = Client(base_url='https://bsky.social')
        bsky_client.login(os.environ['BSKY_USER'], os.environ['BSKY_PASSWORD'])
        print('Logged in to Bluesky.')

    while True:
        for rss_url in RSS_URLS:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if 'console' in PLATFORMS:
                    post_to_console(entry)
                if entry.id in old_entries:
                    pass
                elif (calendar.timegm(feed.entries[0].published_parsed) < start_time):
                    old_entries.append(entry.id)
                else:
                    if 'bluesky' in PLATFORMS:
                        post_to_bluesky(entry)
                    if 'mastodon' in PLATFORMS:
                        post_to_mastodon(entry)
                    old_entries.append(entry.id)
        time.sleep(REFRESH_INTERVAL)
