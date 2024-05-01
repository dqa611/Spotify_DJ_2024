# %%


import pandas as pd
import os
from QuocAnh_py.others.utilities import import_json, print_this_msg
from QuocAnh_py.spotify.spotify_playlist_import_export import import_playlists


# %%


def import_settings(print_msg: bool = False):
    if os.path.exists("./settings/settings_manual.json"):
        print_this_msg(print_msg, "Importing settings from settings_manual.json")
        return import_json("./settings/settings_manual.json")
    else:
        print_this_msg(print_msg, "Importing settings from settings_default.json")
        return import_json("./settings/settings_default.json")


# %%


def get_df(
    playlist_import: bool,
) -> pd.DataFrame:

    settings = import_settings()["paths"]
    default_playlists = settings["default_input"]
    default_data = settings["default_data"]

    if playlist_import:
        print(f"Importing Spotify playlists from {default_playlists}")
        playlist_ids = pd.read_csv(default_playlists)
        if len(playlist_ids) == 0:
            raise ValueError(f"No playlist_ids found in {default_playlists}")

        df = import_playlists(list(playlist_ids["playlist_ids"]))
        df.to_csv(default_data)
    else:
        print(f"Getting the Spotify playlist data from {default_data}")

    df = pd.read_csv(default_data).set_index("track_id")
    return df
