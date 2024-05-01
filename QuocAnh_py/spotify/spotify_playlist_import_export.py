# %%

import pandas as pd

from QuocAnh_py.spotify.spotify_api import sp, USERNAME_ID
from QuocAnh_py.spotify.spotify_crawling import (
    get_playlist_tracks,
    get_tracks_data_from_playlist,
)

from QuocAnh_py.others.utilities import convert_ms


# %%


def import_playlists(playlist_ids: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for playlist_id in playlist_ids:
        playlist = get_playlist_tracks(playlist_id)
        print(f"Playlist '{playlist['name']}' imported successfully")
        df = pd.concat([df, get_tracks_data_from_playlist(playlist)])  # type: ignore

    # Additional steps
    df = df.T.drop_duplicates().T.reset_index(drop=True).set_index("track_id")

    df["duration_min"] = df["duration"].apply(lambda x: convert_ms(x)[1])
    # Translate the key to the corresponding key
    # Import here to avoid circular import error
    from QuocAnh_py.models.harmonic_keys import key_translate

    df["translated_key"] = df.apply(
        lambda row: key_translate(row["key"], row["mode"]), axis=1
    )
    df["year_released"] = pd.to_datetime(df["album_releasedate"]).dt.year

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
