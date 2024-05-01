# %%


import pandas as pd
from QuocAnh_py.execute.init import import_settings
import QuocAnh_py.others.shortcuts as sc
import QuocAnh_py.others.utilities as ult


# %%
# Get the list of harmonic keys from a track using the Camelot key system
# In Spotify data
# For mode, 1 is major, 0 is minor
# For key, 0 is C. 1 is C#. 12 keys. So it goes from 0 to 11


# %%


def key_number_translate(key: int) -> str:
    if key > 11:
        raise ValueError("Movement must be from 0 to 11")
    key_mapping = {
        0: "C",
        1: "C#",
        2: "D",
        3: "D#",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "G#",
        9: "A",
        10: "A#",
        11: "B",
    }
    # -1 is the default value if the key is not found
    return key_mapping.get(key, -1)  # type: ignore


# %%


def mode_number_translate(mode: int) -> str:
    if mode > 1:
        raise ValueError("Movement must be either 0 or 1")
    mode_mapping = {0: "m", 1: ""}
    # -1 is the default value if the key is not found
    return mode_mapping.get(mode, -1)  # type: ignore


# %%


def key_translate(key: int, mode: int) -> str:
    return "".join([key_number_translate(key), mode_number_translate(mode)])


# %%


def key_mvmtment(key: int, movement: int) -> int:
    if key > 11 or key < 0:
        raise ValueError("Key must be from 0 to 11")
    return (key + movement) % 12


# %%


def mode_mvmtment(mode: int, movement: int) -> int:
    if mode > 1:
        raise ValueError("Mode must be either 0 or 1. 1 is major, 0 is minor")
    if movement > 1 or movement < 0:
        raise ValueError("Movement must be either 0, 1")
    return abs(mode - movement)


# %%
# The movement here is based on the Camelot wheel


def calculate_mood(input_mode: int, mode_mvmt: int) -> int:
    if mode_mvmt == 0:
        mood = 0
    else:
        # for mode, 1 is major, 0 is minor
        if input_mode == 0:
            # minor to major
            mood = 1
        else:
            # major to minor
            mood = -1

    return mood


# %%
# The movement here is based on the Camelot wheel


def calculate_energy(key_mvmt: int) -> int:
    if key_mvmt == 0:
        energy = 0
    # move clockwise in the camelot wheel
    elif key_mvmt > 0:
        energy = 1
    # move counter clockwise in the camelot wheel
    else:
        energy = -1

    return energy


# %%


def translate_energy(energy: int) -> str:
    energy_interpretation = import_settings()["models"]["harmonic_keys"]["input"][
        "energy_interpretation"
    ]
    if energy == 0:
        return energy_interpretation["0"]
    elif energy == 1:
        return energy_interpretation["1"]
    else:
        return energy_interpretation["-1"]


# %%


def translate_mood(mood: int) -> str:
    mood_interpretation = import_settings()["models"]["harmonic_keys"]["input"][
        "mood_interpretation"
    ]
    if mood == 0:
        return mood_interpretation["0"]
    elif mood == 1:
        return mood_interpretation["1"]
    else:
        return mood_interpretation["-1"]


# %%
# Return harmonic mixing options for a given key and mode. The rules are in the settings.json


def get_harmonic_scale(key: int, mode: int) -> list:
    settings = import_settings()["models"]["harmonic_keys"]["input"]
    harmonic_rules = settings["harmonic_rules"]
    applied_rules = settings["applied"]

    harmonic_scale = [
        (rule["key_mvmt"], rule["mode_mvmt"], name, rule["camelot_mvmt"])
        for name, rule in harmonic_rules.items()
        if name in applied_rules
    ]

    return harmonic_scale


# %%
# Return harmonic mixing options for a given key and mode


def harmonic_scale_output(key: int, mode: int) -> pd.DataFrame:
    harmonic_scale = get_harmonic_scale(key, mode)

    result = []
    for key_mvmt, mode_mvmt, desc, camelot_mvmt in harmonic_scale:
        key_compatible = key_mvmtment(key, key_mvmt)
        mode_compatible = mode_mvmtment(mode, mode_mvmt)
        energy_mvmt = calculate_energy(camelot_mvmt)
        mood_mvmt = calculate_mood(mode, mode_mvmt)
        translated_energy = translate_energy(energy_mvmt)
        translated_mood = translate_mood(mood_mvmt)
        result.append(
            (
                key_compatible,
                mode_compatible,
                camelot_mvmt,
                translated_energy,
                translated_mood,
                energy_mvmt,
                mood_mvmt,
                desc,
            )
        )
    df = pd.DataFrame(
        result,
        columns=[
            "key_compatible",
            "mode_compatible",
            "camelot_mvmt",
            "translated_energy",
            "translated_mood",
            "energy_mvmt",
            "mood_mvmt",
            "desc",
        ],
    )

    return df


# %%
# Return tracks that match the scale. Variable harmonic_scales needs to have key_compatible and mode_compatible columns.


def run_harmonic_tracks(
    df: pd.DataFrame,
    input_index: str,
    grouped: bool = False,
    print_add_cols: bool = False,
    drop_dups_cols: bool = True,
) -> pd.DataFrame:
    """This function could return 2 DataFrame options. If grouped is False, it will return the merged DataFrame, where each track is in its own row. If grouped is True, it will return the grouped DataFrame, where the track_id are grouped as list in a single row per scale.

    The grouped view is more for debugging and presentation. While the ungrouped view is for further processing.

    The print additional column view is only available for the ungrouped view
    """

    key, mode = ult.get_data_from_index(df, input_index, "key", "mode")
    harmonic_scales = harmonic_scale_output(key, mode)

    # Harmonic Keys doesn't require settings input. The input is key and mode
    df = df.reset_index().rename(columns={"index": "track_id"})

    # Print additional columns for presentation
    print_cols = ["track_id", "track_name", "key", "mode"]
    if print_add_cols:
        print_cols += sc.get_quick_track_info()

    merged_df = pd.merge(
        df[print_cols],
        harmonic_scales,
        left_on=["key", "mode"],
        right_on=["key_compatible", "mode_compatible"],
    )

    if grouped:
        merged_df = pd.merge(
            df[["track_id", "track_name", "key", "mode"]],
            harmonic_scales,
            left_on=["key", "mode"],
            right_on=["key_compatible", "mode_compatible"],
        )
        grouped_df = (
            merged_df.groupby(["key_compatible", "mode_compatible"])
            .agg({"track_id": list, "track_name": list})
            .reset_index()
        )
        harmonic_tracks = pd.merge(
            harmonic_scales, grouped_df, on=["key_compatible", "mode_compatible"]
        )

        harmonic_tracks["translated_key"] = harmonic_tracks.apply(
            lambda x: key_translate(x["key_compatible"], x["mode_compatible"]), axis=1
        )

        # Flip the columns order for easieer read
        return harmonic_tracks.iloc[:, ::-1]

    df_final = merged_df.set_index("track_id")
    if drop_dups_cols:
        return df_final.drop(columns=["key", "mode", "track_name"])
    return df_final


# %%


# def get_scale_dict():
#     scale_dict = {
#         1: ("tonic", ["rest", "resolution", "completion", "stability", "tranquility"]),
#         2: ("supertonic", ["preparation", "build-up"]),
#         3: ("mediant", ["transition", "departure", "change"]),
#         4: ("subdominant", ["preparation", "transition", "departure"]),
#         5: ("dominant", ["raise", "tension", "instability"]),
#         6: ("submediant", ["raise", "instability", "tension"]),
#         7: ("leading tone", ["preparation", "transition"]),
#     }

#     return scale_dict
