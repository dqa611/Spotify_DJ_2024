# %%


import pandas as pd
import numpy as np
from typing import Optional, Union, List


# %%


def randomize_index(
    df: pd.DataFrame = None,
    excluded: Optional[list] = None,
    type: Union[List[float], int] = 0,
    msg_only: bool = False,
) -> Union[tuple, str]:
    """
    This function will randomize the index of the DataFrame. It will return the index, the result, and an optional message. The type is either 0, 1 or a list. If 0, it will select the first index. If 1, it will sample equally. If a list, it will sample with weights. It will favor the top results with the input additional weights. In the event where the result length is shorter than the list of the additional weights, it will use the favor weights equal to the size of the result length. Lastly, if the DataFrame is empty, it will raise an error. If the list is empty, it will raise an error.
    """
    if msg_only:
        if type == 0:
            return "by selecting the first index"
        elif type == 1:
            return "by sampling all result tracks equally"
        elif isinstance(type, list):
            return f"by sampling with weights. Favor the top {len(type)} results with these additional weights: {type}"
        else:
            raise ValueError("Invalid type detected")

    df = df[~df.index.isin(excluded)]

    if type == 0:
        random_index = df.index[0]
    elif type == 1:
        random_index = df.sample().index[0]
    elif isinstance(type, list):
        n_favor = len(type)
        n_df = len(df)

        if n_favor == 0:
            raise ValueError("Empty list detected'")
        if n_df == 0:
            raise ValueError("Empty DataFrame detected'")
        else:
            weights = [
                1 / n_df + type[i] if i < min(n_df, n_favor) else 1 / n_df
                for i in range(n_df)
            ]
            total_weight = sum(weights)
            norm_weights = [weight / total_weight for weight in weights]

        random_index = df.sample(weights=norm_weights).index[0]

    result = df[df.index == random_index]

    return random_index, result
