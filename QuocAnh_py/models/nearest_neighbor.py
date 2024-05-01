# %%


from sklearn.neighbors import NearestNeighbors
import pandas as pd

import QuocAnh_py.others.utilities as ult
import QuocAnh_py.others.shortcuts as sc
from QuocAnh_py.execute.init import import_settings


# %%
def nearest_neighbor(
    data: pd.DataFrame,
    index_input: str,
    nn_number_of_output: int,
) -> tuple:

    # Normalize the data before running the model
    data = ult.normalize_data(data)
    model = NearestNeighbors(n_neighbors=nn_number_of_output).fit(data)
    index = data[data.index.isin([index_input])]
    distances, indices = model.kneighbors(index)

    return distances, indices


# %%


def proccess_nearest_neighbor(df: pd.DataFrame, nn_result: tuple) -> pd.DataFrame:

    nn_tracks = df.iloc[nn_result[1].flatten()].copy()

    nn_tracks.loc[:, "nn_score"] = nn_result[0].flatten()
    nn_tracks = nn_tracks.sort_values(by="nn_score", ascending=True)
    nn_tracks.loc[:, "nn_index_position"] = [
        nn_tracks.index.get_loc(i) for i in nn_tracks.index
    ]

    return nn_tracks


# %%


def run_nearest_neighbor(
    df: pd.DataFrame,
    index_input: str,
    print_add_cols: bool = False,
    print_input_msg: bool = False,
) -> pd.DataFrame:

    settings = import_settings()["models"]
    nn_input = settings.get("nearest_neighbor", {}).get("input", {})

    nn_number_of_output = nn_input["nn_number_of_output"]
    # Cap this so it doesn't take too long
    if nn_number_of_output > 15:
        nn_number_of_output = 15

    nn_metrics = nn_input["nn_metrics"]
    max_cap_score = nn_input["max_cap_score"]
    return_percentile = nn_input["return_percentile"]
    percentile_ascending = nn_input["percentile_ascending"]
    print_cols = ["nn_score", "nn_index_position"]

    if print_add_cols:
        print_cols += sc.get_quick_track_info() + sc.get_nn_input_cols()

    # Run the nearest neighbor
    nn_result = nearest_neighbor(df[nn_metrics], index_input, nn_number_of_output)
    nn_df = proccess_nearest_neighbor(df, nn_result)  # type: ignore

    # Filter the results
    return ult.top_percentile(
        nn_df[print_cols],
        "nn_score",
        max_cap=max_cap_score,  # type: ignore
        return_percentile=return_percentile,  # type: ignore
        percentile_ascending=percentile_ascending,  # type: ignore
    )


# %%
