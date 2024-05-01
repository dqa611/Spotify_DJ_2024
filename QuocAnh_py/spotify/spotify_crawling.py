# %% [markdown]
# Functions to get Spotify playlist data using Spotify API. The notebook will get the following data:
# For more information, please visit https://spotipy.readthedocs.io/en/latest/. Watch https://www.youtube.com/watch?v=vipVEWe86Lg&t=242s for more information
# Note: Spotify API limits the number of tracks pulled up to 49 tracks. Therefore, the notebook contains a loop to automate this process

# %%
from QuocAnh_py.spotify.spotify_api import sp
import pandas as pd


# %%
# Collect data of a track from its json data


def get_tracks_data(data: dict) -> dict:
    return {
        "track_name": data["name"],
        "track_id": data["id"],
        "artist": data["artists"][0]["name"],
        "artist_id": data["artists"][0]["id"],
        "album": data["album"]["name"],
        "album_id": data["album"]["id"],
        "album_releasedate": data["album"]["release_date"],
        "track_popularity": data["popularity"],
        "duration": data["duration_ms"],
    }


# %%
# Collect data of a track from its json data


def get_tracks_audio_features(data: dict) -> dict:
    return {
        "danceability": data["danceability"],
        "energy": data["energy"],
        "key": data["key"],
        "loudness": data["loudness"],
        "mode": data["mode"],
        "speechiness": data["speechiness"],
        "acousticness": data["acousticness"],
        "instrumentalness": data["instrumentalness"],
        "liveness": data["liveness"],
        "valence": data["valence"],
        "tempo": data["tempo"],
        "track_id": data["id"],
    }


# %%
# Get Playlist Data


def get_playlist_data(data: dict) -> dict:
    return {
        "playlist_id": data["id"],
        "playlist_name": data["name"],
        "playlist_owner": data["owner"]["display_name"],
        "playlist_owner_id": data["owner"]["id"],
    }


# %%
# Get the list of tracks from a playlist


def get_playlist_tracks(playlist_id: str) -> dict:
    playlist = sp.playlist(playlist_id)

    print(playlist["name"])
    print("Total tracks", playlist["tracks"]["total"])

    return playlist  # type: ignore


# %%
# Search a track data by track name, artist and album


def get_track_data_from_search(
    track_name: str, artist: str = "{}", album: str = "{}"
) -> dict:

    search_result = sp.search(
        q=f"album: {album} artist: {artist} track: {track_name}",
        limit=1,
        type="track",
        market="US",
    )
    # Return just top search to reduce processing
    return search_result["tracks"]["items"][0]  # type: ignore

# %%

def search_track_on_spotify(track_name: str, artist: str = "{}", album: str="{}") -> tuple:
    
    result = get_track_data_from_search(track_name, artist, album)
    track_name = result['name']
    track_id = result['id']
    artists = [x['name'] for x in result['artists']]
    album = result['album']['name']
    
    print(f"Track: {track_name}  by {artists}. Album: {album}. Track ID {track_id}")
    return track_id, track_name, artists, album


# %%
# Search a track data by track name, artist and album


def get_artist(artist_id: str) -> dict:

    search_result = sp.artist(artist_id)
    return {
        "artist": search_result["name"],
        "arist_id": search_result["id"],
        "artist_genres": " | ".join([genre for genre in search_result["genres"]]),
        "artist_popularity": search_result["popularity"],
    }


# %%
# Get Data from Tracks of a Playlist Data


def get_tracks_data_from_playlist(data: dict) -> pd.DataFrame:

    playlist_data = get_playlist_data(data)

    playlist_tracks_data = data["tracks"]["items"]
    playlist_df = pd.DataFrame()

    for data in playlist_tracks_data:
        track_data = get_tracks_data(data["track"])

        track_id = track_data["track_id"]
        track_audio = sp.audio_features(track_id)[0]  # type: ignore
        tracks_audio = get_tracks_audio_features(track_audio)

        artist_id = track_data["artist_id"]
        artist_data = get_artist(artist_id)

        track_df = [
            {
                **track_data,
                **tracks_audio,
                **artist_data,
                **playlist_data,
            }
        ]
        track_df = pd.DataFrame.from_dict(track_df)  # type: ignore
        playlist_df = pd.concat([playlist_df, track_df], axis=0)

    return playlist_df
