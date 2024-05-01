# %%


import os
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
import re
from typing import Optional, Union, List


# %%


def import_json(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


# %%


def export_json(data, path):
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)


# %%


def print_this_msg(print_msg: bool = False, msg: str = ""):
    if print_msg:
        print(msg)


# %%


def get_data_from_search(
    search_keyword: str, search_where: str, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Return DataFrame whom column values match a search keyword in that column. The column is a string.
    Search data from a DataFrame given the search keyword and the column name where the search will be performed.
    """

    # Trim spaces and convert to lowercase
    search_keyword = search_keyword.strip().lower()
    search_where = df.loc[:, search_where]  # type: ignore
    search_where = search_where.str.strip().str.lower()  # type: ignore
    search_this = search_where.str.contains(search_keyword)  # type: ignore
    result = df[search_this]

    if len(result) == 0:
        raise ValueError("No result found")
    if len(result) >= 2:
        print(f"Multiple results found")

    return result


# %%


def get_data_from_index(df: pd.DataFrame, indices: str, *args):
    """
    Return a list of items where the input indices (string) match the DataFrame indices. The args are column names.
    """

    return [df[df.index.str.contains(indices)][col].item() for col in args]


# %%
# Return rows whom columns match an element in a list of inputs. The column value itself is a list.


def get_data_from_a_column_data(
    df: pd.DataFrame, col: str, input: Union[List[str], str]
):
    """
    Return DataFrame where column values match an element in a list of inputs. The column value itself could be a list.
    """

    # If input is a string
    if isinstance(input, str):
        if all(df[col].apply(lambda x: isinstance(x, list))):
            # If the column values are lists
            result = df[df[col].apply(lambda x: input in x)]
        elif all(df[col].apply(lambda x: isinstance(x, str))):
            # If the column values are strings
            result = df[df[col].str.contains(input)]

    if all(df[col].apply(lambda x: isinstance(x, list))):
        # If the column values are lists
        result = df[df[col].apply(lambda x: any(y in x for y in input))]
    elif all(df[col].apply(lambda x: isinstance(x, str))):
        # If the column values are strings
        result = df[df[col].apply(lambda x: x in input)]

    return result


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
def merge_dfs_by_index(dfs: list) -> pd.DataFrame:

    df_final = dfs[0]

    for df in dfs[1:]:
        df_final = df_final.merge(df, left_index=True, right_index=True)

    return df_final


# %%
# Remove special characters


def remove_special_character(input_string: str, replace: str = "") -> str:
    return re.sub("[^A-Za-z0-9 ]+", "", input_string)


# %%


def split_and_process_words(input_word: str, split_str: str = "|") -> list:
    words = str(input_word).lower().split(split_str)
    # Manually replace '-' with space to handle words like 'k-pop'
    words = [s.strip().replace("-", " ") for s in words]
    words = [remove_special_character(s, " ") for s in words]

    return words


# %%
# Extract Substring from a string
def extract_substring(input_string: str, start_char: str = "\\", end_char: str = "?"):
    start = input_string.find(start_char) + 1
    end = input_string.find(end_char)
    if start != -1 and end != -1:
        return input_string[start:end]
    else:
        return ""


# %%


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    if not (isinstance(df, pd.DataFrame) or isinstance(df, pd.Series)):
        raise ValueError("Input is not a DataFrame or Series")
    else:
        scaler = StandardScaler()
        df_normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
        df_normalized.index = df.index

        return df_normalized


# %%


def top_percentile(
    df: pd.DataFrame,
    col: str,
    min_cap: Optional[float] = None,
    max_cap: Optional[float] = None,
    return_percentile: float = 1,
    percentile_ascending: bool = True,
) -> pd.DataFrame:
    if not isinstance(df, (pd.DataFrame, pd.Series)):
        raise ValueError("Input is not a DataFrame or Series")

    if min_cap is not None:
        df = df[df[col] >= min_cap]
    if max_cap is not None:
        df = df[df[col] <= max_cap]

    if return_percentile == 1 or len(df) <= 2:
        return df

    ptile = max(1, int((len(df) - 1) * return_percentile))
    df = df.astype({col: float})
    # nsmallest and nlargest auto sort the DataFrame
    return df.nsmallest(ptile, col) if percentile_ascending else df.nlargest(ptile, col)


# %%
# Handle default input of a dictionary


def default_value_input(
    default_value,
    key: str,
    input_dict: dict,
    print_msg: bool = False,
):
    """
    This function will return the input value if it is not the default value. If the inpuut value is missing, then it will return the default value. The default value lives in a dictionary with keys. If the input value is not the default value, it will print a message. If the input value is a list, it will check if all the elements in the list are the DataFrame's columns (this is optional). If not, it will raise an error.

    Parameters:
    default_value (any): The default value.
    key (str): The key in the dictionary.
    input_dict (dict): The dictionary where the default value lives.

    Returns:
    pd.DataFrame:
    """
    input_value = input_dict.get(key, default_value)
    if input_value != default_value:
        print_this_msg(print_msg, f"Overwriting {key} with {input_value}")
        return input_value
    print_this_msg(print_msg, f"Use default {key} value {default_value}")
    return default_value


# %%
# Convert milliseconds to hours and minutes


def convert_ms(milli: int):
    seconds = (milli / 1000) % 60
    minutes = (milli / (1000 * 60)) % 60
    hours = (milli / (1000 * 60 * 60)) % 24

    hour_read = f"{int(hours)}:{int(minutes)}:{int(seconds)}"
    minute_read = round(int(hours) * 60 + minutes, 2)
    return hour_read, minute_read


# %%


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)
