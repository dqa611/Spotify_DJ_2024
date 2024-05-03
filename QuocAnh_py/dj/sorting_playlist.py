# %%

import pandas as pd
from typing import Optional, Union, List

import QuocAnh_py.others.utilities as ult
from QuocAnh_py.others.utilities import print_this_msg
from QuocAnh_py.execute.init import import_settings
from QuocAnh_py.others.randomize import randomize_index
from QuocAnh_py.dj.best_next_tracks import run_best_next_tracks

# %%
# In this function, introduce randomization for the best next track. The randomization can be done in three ways: 0, 1, or a list. If 0, it will select the first index. If 1, it will sample all result tracks equally. If a list, it will sample with weights. It will favor the top results with the input additional weights. In the event where the result length is shorter than the list of the additional weights, it will use the favor weights equal to the size of the result length. Lastly, if the DataFrame is empty, it will raise an error. If the list is empty, it will raise an error. Visit the randomize.py file for more information.


def add_track_to_playlist(
    df: pd.DataFrame,
    track_id: str,
    used_track: list,
    sorted_playlist: pd.DataFrame,
    total_duration: float,
    randomize_type: list,
    print_msg: bool,
) -> tuple:
    # Remove the input track from the selection
    next_tracks = run_best_next_tracks(
        df,
        track_id,
        used_track,
        remove_input_track=True,
        print_msg=print_msg,
    )

    # Apply randomization
    random_choice = randomize_index(next_tracks, used_track, randomize_type)
    next_track_id, next_track_df = random_choice[0], random_choice[1]

    used_track.append(track_id)  # Adding used track to the list
    sorted_playlist = pd.concat([sorted_playlist, next_track_df]).drop_duplicates()
    total_duration += ult.get_data_from_index(df, next_track_id, "duration_min")[0]

    return next_track_id, sorted_playlist, total_duration, used_track


# %%


def add_tracks_until_max_duration(
    df: pd.DataFrame,
    first_track_id: str,
    used_track: list,
    sorted_playlist: pd.DataFrame,
    total_duration: float,
    max_duration: float,
    order: int,
    randomize_type: list,
    print_msg: bool,
) -> tuple:
    while total_duration < max_duration:
        print_this_msg(
            print_msg,
            f"Searching {ult.get_data_from_index(df, first_track_id, 'track_name')}'s best next track",
        )

        next_track_id, sorted_playlist, total_duration, used_track = (
            add_track_to_playlist(
                df,
                first_track_id,
                used_track,
                sorted_playlist,
                total_duration,
                randomize_type,
                print_msg,
            )
        )
        first_track_id = next_track_id
        sorted_playlist = sorted_playlist.copy()  # To avoid SettingWithCopyWarning
        order += 1
        sorted_playlist.loc[next_track_id, "order"] = order
    return sorted_playlist, total_duration, order


# %%


def choose_randomization_type(print_msg: bool = False):
    print_this_msg(print_msg, "Apply randomization from settings.json")
    type = import_settings()["preferences"]["randomize"]["applied"]
    print_this_msg(
        print_msg,
        "Choosing the best next track " + randomize_index(type, msg_only=True),
    )
    return type


# %%


def sort_playlist(
    df: pd.DataFrame,
    track_id: str,
    print_msg: bool = False,
) -> pd.DataFrame:
    used_track = []
    first_track = run_best_next_tracks(df, track_id, print_msg=print_msg)
    first_track_id = first_track.iloc[0].name
    print_this_msg(
        print_msg,
        f"Track input {first_track_id}, '{ult.get_data_from_index(df, first_track_id,'track_name')}'",
    )

    total_duration = ult.get_data_from_index(df, track_id, "duration_min")[0]
    sorted_playlist = first_track.iloc[[0]]
    max_duration = import_settings()["preferences"]["length_min"]
    order = 0
    randomize_type = choose_randomization_type(print_msg)
    sorted_playlist = sorted_playlist.copy()  # To avoid SettingWithCopyWarning
    sorted_playlist.loc[first_track_id, "order"] = order

    sorted_playlist, total_duration, order = add_tracks_until_max_duration(
        df,
        first_track_id,
        used_track,
        sorted_playlist,
        total_duration,
        max_duration,
        order,
        randomize_type,
        print_msg,
    )
    print_this_msg(
        print_msg,
        f"Playlist sorted successfully. Total duration: {round(total_duration)} minutes",
    )

    sorted_playlist = sorted_playlist.drop(columns=df.columns.intersection(sorted_playlist.columns))

    final_df = df.merge(
        sorted_playlist, how="inner", left_index=True, right_index=True
    ).sort_values("order")

    final_df["cum_duration"] = final_df["duration_min"].cumsum()

    return final_df
