import re, requests

def extract_playlist_id_from_link(link):
    long_url_regex = r'(?:spotify:playlist:|open\.spotify\.com\/playlist\/)([a-zA-Z0-9]+)'
    short_url_regex = r'(?:spotify\.link\/)([a-zA-Z0-9]+)'

    long_url_match = re.search(long_url_regex, link)
    short_url_match = re.search(short_url_regex, link)

    if long_url_match:
        return long_url_match.group(1)
    elif short_url_match:
        short_url = f'https://spotify.link/{short_url_match.group(1)}'
        try:
            response = requests.head(short_url, allow_redirects=True)
            long_url = response.url
            return extract_playlist_id_from_link(long_url)
        except Exception as e:
            print(f"Error resolving short URL: {e}")
            return None
    else:
        return None