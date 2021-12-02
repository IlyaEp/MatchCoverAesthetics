import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


data = []

ids = set()
def process(filename):
    f = open(filename)
    js = f.read()
    f.close()
    mpd_slice = json.loads(js)

    for playlist in mpd_slice["playlists"]:
        for track in playlist["tracks"]:
            track_id = track["track_uri"].replace('spotify:track:', '')
            ids.add(track_id)

def get_tracks():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="efe92dae05ec4fb5838724f9389e30a5",
                                                               client_secret="b515f27d598949dc96b066ab58085cbc"))
    for track_id in ids:
        track = sp.track(track_id)
        if track["album"]["images"] == []:
            continue

        artists = []
        for artist in track["artists"]:
            artists.append(artist["name"])
        artists = " & ".join(artists)

        data.append(
            {"track_name": track["name"], "track_artists": artists, "track_id": track["id"],
            "album_cover": track["album"]["images"][0]["url"]})

 
if __name__ == "__main__":
    process('mpd.slice.225000-225999.json')
    #process('mpd.slice.622000-622999.json')
    #process('mpd.slice.996000-996999.json')
    #process('mpd.slice.995000-995999.json')

    get_tracks()
    with open(f'{len(data)}_tracks_no_playlists.json', 'w') as fj:
        json.dump(data, fj)

