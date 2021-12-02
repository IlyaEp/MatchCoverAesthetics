import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from tqdm import tqdm
import credentials as cred


playlist_names = set()
data = []


def process(filename):
    f = open(filename)
    js = f.read()
    f.close()
    mpd_slice = json.loads(js)

    for playlist in mpd_slice["playlists"]:
        playlist_names.add(playlist['name'])


def collect_data():
    ids = set()
    for playlist in tqdm(playlists):
        if playlist['playlists']['items'] == []:
            continue

        tracks = sp.playlist_tracks(playlist['playlists']['items'][0]['id'], limit=50, offset=0)
        offset = 0
        if not playlist['playlists']['items'][0]["images"]:
            continue

        while offset == 0 or offset <= tracks["total"] - 50:
            tracks = sp.playlist_tracks(playlist['playlists']['items'][0]['id'], limit=50, offset=offset)

            for track in tracks["items"]:
                if track["track"] is None:
                    continue

                if track["track"]["id"] in ids or track["track"]["album"]["images"] == []:
                    continue

                artists = []
                for artist in track["track"]["artists"]:
                    artists.append(artist["name"])
                artists = " & ".join(artists)

                data.append(
                    {"track_name": track["track"]["name"], "track_artists": artists, "track_id": track["track"]["id"],
                     "album_cover": track["track"]["album"]["images"][0]["url"],
                     "playlist_name": playlist['playlists']['items'][0]["name"],
                     "playlist_id": playlist['playlists']['items'][0]["id"],
                     "playlist_cover": playlist['playlists']['items'][0]["images"][0]["url"]})

                ids.add(track["track"]["id"])
            offset += 50


if __name__ == "__main__":
    client_id = config.CLIENT_ID
    client_secret = config.CLIENT_SECRET

    auth_manager = spotipy.SpotifyOAuth(client_id=client_id,
                                        client_secret=client_secret,
                                        redirect_uri='http://localhost:8888/callback/')
    sp = spotipy.Spotify(auth_manager=auth_manager)

    process("mpd.slice.510000-510999.json")
    #process("mpd.slice.622000-622999.json")
    #process("mpd.slice.996000-996999.json")

    playlists = []
    for playlist_name in tqdm(playlist_names):
        qeury = 'playlist:' + playlist_name
        playlists.append(sp.search(q=qeury, type='playlist'))


    with open(f'{len(playlists)}_playlists.json', 'w') as f:
        json.dump(playlists, f)

    collect_data()

    with open(f'{len(data)}_tracks_search_method.json', 'w') as f:
        json.dump(data, f)

