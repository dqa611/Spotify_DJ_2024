# %%
import pandas as pd
from typing import Union
from QuocAnh_py.dj.sorting_playlist import sort_playlist
import QuocAnh_py.others.plots as myplts

import QuocAnh_py.spotify.spotify_crawling as spc
from QuocAnh_py.spotify.spotify_playlist_import_export import export_playlist
from QuocAnh_py.execute.init import import_settings, get_df


# %%


def main_func(
    input: Union[tuple, str], playlist_title: str = "My Mixtape Vol.1"
) -> pd.DataFrame:
    """
    This is the main function to run the DJ Playlist. It will sort the playlist based on the input track and export the playlist to a CSV file and/or a Spotify playlist. For all the settings, please refer to the settings.json file. The settings can be changed in the settings.json file or in the widgets in the Jupyter Notebook.
    Please note that the input track has to be in the imported playlist.
    Refer to the README.md for more information
    Input (string or tuple). The input is either the track ID or a tuple of track name, artist, and album.
    Playlist Title (string). The title of the playlist to be exported.
    """

    # Settings
    settings = import_settings()
    print_msg = settings["print_log"]
    print_plt = settings["print_plot"]
    playlist_import = settings["import_from_spotify"]
    playlist_to_csv = settings["export_to_csv"]
    playlist_to_spotify = settings["export_to_spotify"]

    # Import
    df = get_df(playlist_import)

    if isinstance(input, tuple):
        track_name, artist, album = input
        track_id = spc.search_track_on_spotify(track_name, artist, album)[0]
    elif isinstance(input, str):
        track_id = input

    # 04/2024. As of this date. The feature to add a track not from the data imported is not ready yet. The input track for not has to be in the import.
    if track_id not in df.index:
        raise ValueError(
            f"Track ID not in imported dataset. Please add it to the imported playlist before proceeding"
        )

    # DJ Playlist
    my_playlist = sort_playlist(df, track_id, print_msg)
    print(f"My Playlist was created successfully.")

    # Plot
    if print_plt:
        # Import Playlist Plots
        print(f"Printing Pairplot of the imported playlist")
        myplts.corre_plot(df, track_id, "Imported Playlist")

        print(f"Printing WordCloud of the imported playlist")
        myplts.wordcloud_plot(df["artist_genres"])

        # My Playlist Plots
        print(f"Printing My Playlist Summary")
        myplts.playlist_summary(my_playlist)

        print(f"Printing WordCloud of the My Playlist")
        myplts.wordcloud_plot(my_playlist["artist_genres"])

        print(f"Printing My Playlist")
        myplts.plot_my_playlist(my_playlist, playlist_title)

    # Export
    if playlist_to_csv:
        my_playlist.to_csv(f"./data/{playlist_title}.csv")
        print(f"Exported {playlist_title}.csv successfully.")
    if playlist_to_spotify:
        export_playlist(playlist_title, my_playlist.index.tolist())
        print(f"Exported {playlist_title} successfully.")

    return my_playlist


# %%
