# %%


def get_audio_features() -> list:
    return [
        "danceability",
        "energy",
        # "loudness",
        # "speechiness",
        "acousticness",
        # "instrumentalness",
        # "liveness",
        "valence",
        "tempo",
    ]


# %%


def get_quick_track_info() -> list:
    return [
        "track_name",
        "artist",
        "artist_genres",
        "translated_key",
        "duration_min",
        "track_popularity",
        "artist_popularity",
    ]


# %%


def get_harmonic_cols() -> list:
    return [
        "translated_energy",
        "translated_mood",
        "energy_mvmt",
        "mood_mvmt",
        "camelot_mvmt",
        "desc",
    ]


# %%


def get_nn_input_cols() -> list:
    return get_audio_features() + ["year_released"]


# %%


def get_nn_cols() -> list:
    return [
        "nn_score",
        "nn_index_position",
    ]


# %%


def get_common_text_cols() -> list:
    return ["word_match_score"]


# %%


def get_best_next_track_results() -> list:
    return (
        ["intersection", "intersection_num"]
        + get_common_text_cols()
        + get_nn_cols()
        + get_harmonic_cols()
    )


# %%
# Use for Pair plot


def corr_plt_cols() -> list:
    return get_audio_features() + [
        "year_released",
        "track_popularity",
        "artist_popularity",
    ]


# %%
# Use for Summary playlist stats plot, after my playlist is created


def summary_stats_cols() -> list:
    cols = (
        get_nn_input_cols()
        + get_nn_cols()
        + ["intersection"]
        + get_common_text_cols()
        + ["camelot_mvmt", "energy_mvmt", "mood_mvmt"]
        + ["year_released", "track_popularity", "artist_popularity"]
    )
    cols.remove("intersection")
    return cols
