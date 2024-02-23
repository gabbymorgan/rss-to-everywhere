import re
import textwrap
import feedparser
from html2text import html2text

url = 'https://denton.social/@coop.rss'
feed = feedparser.parse(url)


def format_rss_to_text(entry, character_limit, hyperlink_max_length):
    html_without_a_tags = re.sub(
        r'<a href=\"(.*?)\".*/a>', r'\1', entry.summary)
    text_from_html = html2text(html_without_a_tags)

    if (hasattr(entry, 'media_content')):
        media_url = entry.media_content[0]["url"]
        too_long_with_media_url = len(
            text_from_html) + min(len(media_url), hyperlink_max_length) > character_limit
        if (len(entry.media_content) > 2 or too_long_with_media_url):
            summary = textwrap.shorten(
                text_from_html, width=character_limit - hyperlink_max_length, placeholder="...")
            return f'{summary}{entry.link}'
        else:
            return f'{text_from_html}{media_url}'
    elif (len(text_from_html) > character_limit):
        summary = textwrap.shorten(
            text_from_html, width=character_limit - hyperlink_max_length, placeholder="...")
        return f'{text_from_html} {entry.link}'
    else:
        return text_from_html


for entry in feed.entries:
    print('id:', entry.id)
    print(format_rss_to_text(entry, 280, 50))
    print("------------------------")
