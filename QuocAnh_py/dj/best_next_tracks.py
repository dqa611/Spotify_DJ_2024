import pandas as pd
import random

import itertools
from typing import Optional, Union, List

import QuocAnh_py.others.utilities as ult
from QuocAnh_py.execute.init import import_settings
from QuocAnh_py.others.utilities import print_this_msg
from QuocAnh_py.models.harmonic_keys import run_harmonic_tracks, harmonic_scale_output
from QuocAnh_py.models.common_text_score import run_common_text_score
from QuocAnh_py.models.nearest_neighbor import run_nearest_neighbor
from QuocAnh_py.others.randomize import randomize_index
import QuocAnh_py.others.shortcuts as sc


# %%
# In the future, more categories could be added in here. As of 04/2024, it's 3: common genre, harmonic keys, and nearest neighbor.


def run_subsets(df: pd.DataFrame, input_index: str, used_track: list = []) -> dict:
    df = df.loc[~df.index.isin(used_track)]

    settings = import_settings()["models"]
    subsets = {}

    # In settings json, if the applied key is set to True, then the model will be run.
    if settings["common_text_score"]["applied"]:
        subsets["common_text_score"] = run_common_text_score(df, input_index)

    if settings["harmonic_keys"]["applied"]:
        subsets["harmonic_keys"] = run_harmonic_tracks(df, input_index)

    if settings["nearest_neighbor"]["applied"]:
        subsets["nearest_neighbor"] = run_nearest_neighbor(df, input_index)

    subset_dfs = {name: subset for name, subset in subsets.items()}
    subset_indices = {name: list(subset.index) for name, subset in subsets.items()}
    # Make sure the input index is in all the subsets
    check_if_index_in_subsets(subset_indices, input_index)

    return subset_dfs, subset_indices


# %%


def generate_intersection(input_dict: dict) -> dict:
    keys = list(input_dict.keys())
    intersection = dict()

    # Intersection of all keys
    intersection["|".join(keys)] = list(
        set.intersection(*map(set, input_dict.values()))
    )

    # Intersection of combinations of keys. It's dynamicc so it can handle any number of keys. It starts from the largest number of combination pair to the smallest.
    for pair in range(len(keys) - 1, 1, -1):
        for combination in itertools.combinations(keys, pair):
            key = "|".join(combination)
            intersection[key] = list(
                set.intersection(*map(set, (input_dict[k] for k in combination)))
            )

    return intersection


# %%


def check_if_keys_are_in_options(key_list: list):
    settings = import_settings()["models"]
    options = [model for model in settings.keys() if settings[model]["applied"] == True]

    flat = list(itertools.chain.from_iterable([x.split("|") for x in key_list]))
    if not all(check in options for check in flat):
        raise KeyError(
            f"Key {key_list} contains invalid options. Valid options are {options}"
        )


# %%


def check_if_index_in_subsets(df, input_index: str):
    if isinstance(df, dict):
        for key, sublist in df.items():
            if input_index not in (sublist if isinstance(sublist, list) else [sublist]):
                raise ValueError(
                    f"Error: {input_index} not found in dictionary item {key}"
                )
    elif isinstance(df, list):
        if input_index not in df:
            raise ValueError(f"Error: {input_index} not found in any list item")


# %%


def intersection_selection_algorithm(
    df: pd.DataFrame,
    input_index: str,
    intersection: dict,
    preferred_order: Optional[list] = [],
    print_msg: bool = False,
) -> tuple:
    # Make sure the input index is in all the subsets
    check_if_index_in_subsets(intersection, input_index)
    check_if_keys_are_in_options(list(intersection.keys()))

    # Step 1: Return the intersection of all keys if it has more than 1 index and the input index is in it
    max_key = max(intersection.keys(), key=lambda k: k.count("|"))
    if len(intersection.get(max_key, [])) > 1:
        print_this_msg(print_msg, f"Selecting the intersection of all keys: {max_key}")
        return max_key, intersection[max_key]
    else:
        print_this_msg(
            print_msg,
            f"The model results from '{ult.get_data_from_index(df, input_index, 'track_name')}' don't have any intersection besides the input index. Moving on to applying preferred order",
        )
        if preferred_order is None:
            preferred_order = [
                "|".join(comb) for comb in itertools.combinations(options, 2)
            ]
            random.shuffle(preferred_order)
            print_this_msg(
                print_msg,
                f"No preferred order is chosen. A random order will be selected: {preferred_order}",
            )
        while preferred_order:
            key = preferred_order.pop(0)
            if key not in intersection:
                raise ValueError(f"Key {key} is not in the intersection combination")
            else:
                if len(intersection[key]) > 1 and input_index in intersection[key]:
                    print_this_msg(print_msg, f"Select track from intersection: {key}")
                    return key, intersection[key]
                else:
                    print_this_msg(
                        print_msg,
                        f"Key {key} has no intersection or the input index is not in it",
                    )

    # Step 3: If none of the intersection have more than one value other than the index input, select randomly from the original DataFrame
    random_index = random.choice(df.index.tolist())
    print_this_msg(
        print_msg,
        f"None of the intersection have more than one value other than the input index. Selecting a random index: {random_index}, {ult.get_data_from_index(df, random_index, 'track_name')}",
    )
    return "random", [input_index, random_index]  # Alaways include the input_index


# %%


def choose_preference_order(print_msg: bool = False):
    # Manual preferred order is input from the settings json, with the setting 'applied' to True
    settings = import_settings()["preferences"]["preferred_order"]
    models = import_settings()["models"]
    applied_models = [key for key in models.keys() if models[key]["applied"]]

    if settings["applied"]:
        order = settings["order"]
        order = [
            element
            for element in order
            if all(model in applied_models for model in element.split("|"))
        ]

        return order
    else:
        print_this_msg(print_msg, f"Preferred order is not applied")
        return None


# %%


def run_best_next_tracks(
    df: pd.DataFrame,
    track_id: str,
    used_track: list = [],
    remove_input_track: bool = False,
    print_add_cols: bool = False,
    print_msg: bool = False,
) -> pd.DataFrame:
    """
    This function selects the best next track based on models selected in the settings json.

    Parameters:
    df_use (pd.DataFrame): The DataFrame containing the tracks.
    track_id (str): The ID of the selected track.
    used_tracks (list): The list of tracks of excluded tracks from the DataFrame. Default is an empty list.
    remove_input_track (bool): If True, the input track will be included in the output DataFrame.
    print_msg (bool): If True, the message of how the tracks are selected will be printed. Default is False.

    Returns:
    pd.DataFrame: The DataFrame containing the best next track.
    """

    # First, remove tracks not wanted in the df_use
    df_use = df.loc[~df.index.isin(used_track)]

    subset_dfs, subset_indices = run_subsets(df_use, track_id, used_track)
    preferred_order = choose_preference_order(print_msg)

    # Get the intersection result
    intersection_key, intersection_list = intersection_selection_algorithm(
        df_use,
        track_id,
        generate_intersection(subset_indices),
        preferred_order,
        print_msg,
    )

    # Merge the DataFrames based on the key combination
    result_cols = sc.get_best_next_track_results()

    if intersection_key == "random":
        merged_df = df_use.loc[intersection_list]
        merged_df.loc[:, result_cols] = None
    else:
        merged_df = pd.concat(subset_dfs.values(), axis=1, join="outer")
        merged_df = merged_df.loc[intersection_list]
        merged_df.loc[:, "intersection"] = intersection_key
        merged_df.loc[:, "intersection_num"] = len(intersection_key.split("|"))

    # Reorder the columns
    if print_add_cols:
        df1 = df_use[sc.get_quick_track_info()]
        df2 = merged_df[result_cols]
        df3 = df_use[sc.get_audio_features()]
        merged_df = ult.merge_dfs_by_index([df1, df2, df3])

    df_final = merged_df.sort_values("nn_score")

    # Remove input track from DataFrame
    if remove_input_track:
        return df_final.loc[~df_final.index.isin([track_id])]

    return df_final
