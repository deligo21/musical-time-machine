import os
from dotenv import load_dotenv

import spotipy
from spotipy import oauth2

import requests
from bs4 import BeautifulSoup


load_dotenv()
url_base = 'https://www.billboard.com/charts/hot-100/'

# # date = input('Which year do you want to travel to? Type the date in this format: YYYY-MM-DD: ')
date = '2023-02-11'

response = requests.get(url_base + date)
response.raise_for_status()

billboard_html = response.text
soup = BeautifulSoup(billboard_html, 'html.parser')

# first_hit = soup.select_one("li #title-of-a-story").getText().strip()
# print(first_hit)
class_no1 = "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet"
class_no2_100 = "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
# Get all span tags containing articles
list_items = soup.find_all("h3", {"id": "title-of-a-story", "class":[class_no1, class_no2_100]})

top100_list = [song.getText().strip() for song in list_items]
print(top100_list)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
scope = 'playlist-modify-private'
cache = '.spotipyoauthcache'

sp = spotipy.Spotify(
    auth_manager = oauth2.SpotifyOAuth(
        scope = "playlist-modify-private",
        redirect_uri = "http://localhost:8888/callback",
        client_id = client_id,
        client_secret = client_secret,
        show_dialog = True,
        cache_path = "token.txt"
    )
)

user = sp.current_user()
print(user)
user_id = user["id"]

song_uris = []
year = date.split("-")[0]
for song in top100_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
        

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
# print(playlist)

sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist["id"], tracks=song_uris)