# %%

import pandas as pd
from datetime import datetime as dt

from QuocAnh_py.spotify.spotify_api import sp, USERNAME_ID
from QuocAnh_py.spotify.spotify_crawling import (
    get_playlist_tracks,
    get_tracks_data_from_playlist,
)

from QuocAnh_py.others.utilities import convert_ms


# %%


def process_import_df(df: pd.DataFrame) -> pd.DataFrame:
    # Handle Missing Data
    df["album"] = df["album"].fillna("Unknown")
    df["album_releasedate"] = df["album_releasedate"].fillna("2000-01-01")
    df['artist_genres'] = df['artist_genres'].fillna("Unknown")  
    
    # Add duration min
    df["duration_min"] = df["duration"].apply(lambda x: convert_ms(x)[1])

    # Import here to avoid circular import error
    from QuocAnh_py.models.harmonic_keys import key_translate
    # Translate the key to the corresponding key
    df["translated_key"] = df.apply(
        lambda row: key_translate(row["key"], row["mode"]), axis=1
    )

    # Handle date where only year is provided
    def get_year(date_str):
        if len(date_str) == 4:
            return int(date_str)
        try:
            return pd.to_datetime(date_str, format="%Y-%m-%d", errors='coerce').year
        except ValueError:
            return int(date_str)

    df["year_released"] = df["album_releasedate"].apply(get_year)

    # Handle Dups
    df = df.T.drop_duplicates().T.reset_index(drop=True).set_index("track_id")

    return df


# %%


def import_playlists(playlist_ids: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for playlist_id in playlist_ids:
        playlist = get_playlist_tracks(playlist_id)
        print(f"Playlist '{playlist['name']}' imported successfully")
        df = pd.concat([df, get_tracks_data_from_playlist(playlist)])  # type: ignore
    
    df = process_import_df(df)
    
    return df


# %%


def export_playlist(playlist_name: str, set_track_id: tuple):
    create_new_playlist = sp.user_playlist_create(
        user=USERNAME_ID, name=playlist_name, public=False
    )

    new_playlist_id = create_new_playlist["uri"][17:]

    sp.user_playlist_add_tracks(
        user=USERNAME_ID, playlist_id=new_playlist_id, tracks=set_track_id
    )

    print(f"Playlist {playlist_name} is created successfully!")
