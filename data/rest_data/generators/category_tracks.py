import spotipy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.error import HTTPError
from tqdm import tqdm


def collect_tracks(sp, pl):
    data = []
    tracks = sp.playlist_tracks(pl["id"])
    for track in tracks["items"]:
        try:
            track = track["track"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            artists = " & ".join(artists)

            data.append({"track_name": track["name"],
                         "track_artists": artists,
                         "track_id": track["id"],
                         "album_cover": track["album"]["images"][0]["url"],
                         "playlist_name": pl["name"],
                         "playlist_id": pl["id"],
                         "playlist_cover": pl["images"][0]["url"]})
        except Exception as e:
            print(e)
            continue
    while tracks["next"]:
        tracks = sp.next(tracks)
        for track in tracks["items"]:
            try:
                track = track["track"]
                artists = []
                for artist in track["artists"]:
                    artists.append(artist["name"])
                artists = " & ".join(artists)

                data.append({"track_name": track["name"],
                             "track_artists": artists,
                             "track_id": track["id"],
                             "album_cover": track["album"]["images"][0]["url"],
                             "playlist_name": pl["name"],
                             "playlist_id": pl["id"],
                             "playlist_cover": pl["images"][0]["url"]})
            except Exception as e:
                print(e)
                continue
    return data


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="efe92dae05ec4fb5838724f9389e30a5",
                                                           client_secret="b515f27d598949dc96b066ab58085cbc"))
res = []

for country in [None, "RU", "US", "GB"]:
    cats = sp.categories(country=country)["categories"]

    for item in cats["items"]:
        try:
            pl = sp.category_playlists(item["id"], country=country)["playlists"]
            res.extend(pl["items"])
            while 'next' in pl and pl['next']:
                pl = sp.next(pl)
                res.extend(pl["playlists"]["items"])
        except (HTTPError, spotipy.client.SpotifyException):
            print(item["id"])

    while 'next' in cats and cats['next']:
        cats = sp.next(cats)["categories"]
        for item in cats["items"]:
            try:
                pl = sp.category_playlists(item["id"], country=country)["playlists"]
                res.extend(pl["items"])
                while 'next' in pl and pl['next']:
                    pl = sp.next(pl)
                    res.extend(pl["playlists"]["items"])
            except (HTTPError, spotipy.client.SpotifyException):
                print(item["id"])

data = []

for pl in tqdm(res):
    data.extend(collect_tracks(sp, pl))

