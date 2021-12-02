import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="efe92dae05ec4fb5838724f9389e30a5",
                                                           client_secret="b515f27d598949dc96b066ab58085cbc"))
res = []

list_locales_countries = [("eng_US", "US"), ("eng_GB", "GB"), ("eng_US", None), (None, None)] #eng_US seems to equal to eng_GB

#yyyy-MM-ddTHH:mm:ss.
timestamps = []

for year in range(2011, 2021, 1):
    for month in range(1, 11, 1):
        timestamps.extend([f"{year}-{month}-{day}T09:11:11" for day in range(1, 25, 16)])
timestamps.extend(["2012-10-01T09:11:11", "2020-2-01T09:11:11", "2021-10-01T09:11:11"])


for my_timestamp in timestamps:
    for cur_locale, cur_country in list_locales_countries:
        pl = sp.featured_playlists(locale=cur_locale, country=cur_country, timestamp=my_timestamp)["playlists"]
        offset = 0
        while offset == 0 or offset <= pl["total"] - 50:
            res.extend(sp.featured_playlists(locale=cur_locale, country=cur_country, timestamp=my_timestamp, limit=50, offset=offset)["playlists"]["items"])
            offset += 50

data = []
ids = set()
for playlist in res:
    tracks = sp.playlist_tracks(playlist["id"], limit=50, offset=0)
    offset = 0
    if not playlist["images"]:
        continue

    while offset == 0 or offset <= tracks["total"] - 50:
      tracks = sp.playlist_tracks(playlist["id"], limit=50, offset=offset)

      for track in tracks["items"]:
          if track["track"] is None:
             continue

          if track["track"]["id"] in ids or track["track"]["album"]["images"] == []:
            continue

          artists = []
          for artist in track["track"]["artists"]:
              artists.append(artist["name"])
          artists = " & ".join(artists)


          data.append({"track_name": track["track"]["name"], "track_artists": artists, "track_id": track["track"]["id"],
                      "album_cover": track["track"]["album"]["images"][0]["url"],
                      "playlist_name": playlist["name"],
                      "playlist_id": playlist["id"],
                      "playlist_cover": playlist["images"][0]["url"]})

          ids.add(track["track"]["id"])
      offset += 50

with open(f'{len(data)}_tracks.json', 'w') as f:
    json.dump(data, f)
