# %%


import pandas as pd
import QuocAnh_py.others.utilities as ult
import QuocAnh_py.others.shortcuts as sc
from QuocAnh_py.execute.init import import_settings


# %%


def score_rules(x_words: list, y_words: list, partial_score_multiplier: float) -> float:
    # Example ['A B', 'C A D', 'E'] and ['A B', 'C E D D F']
    # First step. 'A B' is a perfect match. Count as 1 point.
    perf_match_score = len(set(x_words) & set(y_words))

    # Second step. Look at the non difference words.
    # Next is looking at 'C A D', 'E' and 'C E D D F'.
    x_non_common_words = list(set(x_words).difference(set(y_words)))
    y_non_common_words = list(set(y_words).difference(set(x_words)))
    # Unique words. Down to C,A,D,E and C,E,D,F
    x_non_common_words = set(
        word for phrase in x_non_common_words for word in phrase.split()
    )
    y_non_common_words = set(
        word for phrase in y_non_common_words for word in phrase.split()
    )

    # C,D,E match. Each gets point multiplied by partial_score_multiplier
    partial_match_score = partial_score_multiplier * len(
        x_non_common_words & y_non_common_words
    )

    return perf_match_score + partial_match_score


# %%


def calculate_score(
    input_text: str,
    split_str: str,
    df: pd.DataFrame,
    col: str,
    partial_score_multiplier: float,
) -> pd.DataFrame:
    # Split the word in the input text
    x_words = ult.split_and_process_words(input_text, split_str)
    # Split all the words in each row of the column. This step will apply to all the rows in the original DataFrame
    y_col = df[col].apply(lambda y: ult.split_and_process_words(y, split_str))

    perf_match_score_list = [
        score_rules(x_words, y_words, partial_score_multiplier) for y_words in y_col
    ]

    df_result = df.copy()
    df_result["word_match_score"] = perf_match_score_list

    return df_result


# %%


def run_common_text_score(
    df: pd.DataFrame,
    input_index: str,
    print_add_cols: bool = False,
    print_input_msg: bool = False,
) -> pd.DataFrame:

    # Input parameters are imported from the settings json file
    settings = import_settings()["models"]
    settings = settings.get("common_text_score", {}).get("input", {})
    split_str = settings["split_str"]
    which_col = settings["which_col"]
    partial_score_multiplier = settings["partial_score_multiplier"]
    default_input_index_score = settings["default_input_index_score"]
    min_cap_score = settings["min_cap_score"]
    return_percentile = settings["return_percentile"]
    print_cols = ["word_match_score"]
    if print_add_cols:
        print_cols += sc.get_quick_track_info() + sc.get_nn_input_cols()

    input_text = ult.get_data_from_index(df, input_index, which_col)[0]

    # Calculate the score
    df_result = calculate_score(
        input_text, split_str, df, which_col, partial_score_multiplier
    )

    # The default value of the input index is defined in settings.json. If the input index is not in the DataFrame, then add it back with the default value.
    if input_index not in df_result.index:
        df_result = df[df.index == input_index]
    df_result.loc[df_result.index == input_index, "word_match_score"] = (
        default_input_index_score
    )

    # Use percentile to filter down results
    return ult.top_percentile(
        df_result[print_cols],
        "word_match_score",
        min_cap=min_cap_score,
        return_percentile=return_percentile,
        percentile_ascending=False,
    ).sort_values("word_match_score", ascending=False)
