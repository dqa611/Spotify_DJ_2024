# %%


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Union, List

from QuocAnh_py.others.utilities import rgb_to_hex
from QuocAnh_py.execute.init import import_settings
import QuocAnh_py.others.shortcuts as sc


# %%


def corre_plot(
    df: pd.DataFrame,
    input_index: Union[List[str], str, None] = None,
    title: str = "Pairplot & Histogram of the playlist",
    columns: Optional[List[str]] = None,
):
    if columns is None:
        columns = sc.corr_plt_cols()

    if input_index is not None:
        print(f"Highlighting input indices in the pair plot")
        if isinstance(input_index, str):
            input_index = [input_index]

        df["highlight"] = df.index.map(
            lambda index: "highlight" if index in input_index else "not highlight"
        )

        columns_plt = columns + ["highlight"]
        g = sns.pairplot(
            df[columns_plt], hue="highlight", plot_kws={"label": columns_plt}
        )
    else:
        columns_plt = columns
        g = sns.pairplot(df[columns_plt], plot_kws={"label": columns_plt})

    g.fig.subplots_adjust(top=0.95)  # adjust the Figure in pairplot
    g.fig.suptitle(title, fontsize=25)
    g.legend.set_visible(False)  # type: ignore

    for i in range(len(columns)):
        g.axes[i][0].yaxis.label.set_size(20)
        g.axes[-1][i].xaxis.label.set_size(20)

    return g


# %%


def playlist_summary(df: pd.DataFrame, columns: Optional[List[str]] = None):
    settings = import_settings()["models"]
    default_input_index_score = settings["common_text_score"]["input"][
        "default_input_index_score"
    ]

    if columns is None:
        columns = sc.summary_stats_cols()
        if not settings["nearest_neighbor"]["applied"]:
            columns = [col for col in columns if col not in sc.get_nn_cols()]
        if not settings["common_text_score"]["applied"]:
            columns = [col for col in columns if col not in sc.get_common_text_cols()]
        if not settings["harmonic_keys"]["applied"]:
            columns = [
                col
                for col in columns
                if col not in ["camelot_mvmt", "energy_mvmt", "mood_mvmt"]
            ]

    num_subplots = len(columns)
    grid_size = calculate_grid_size(num_subplots)
    fig, axs = plt.subplots(grid_size[0], grid_size[1], figsize=(15, 15))

    for idx, col in enumerate(columns):
        ax = axs[idx // grid_size[1], idx % grid_size[1]]
        ax.hist(
            df[col].replace(default_input_index_score, 0).fillna(0),
            bins=10,
            edgecolor="black",
        )
        ax.set_title(f"{col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")

    plt.title("Playlist Summary")
    plt.tight_layout()
    return plt


# %%
# Matrix, Bar plot and Line plot


def calculate_grid_size(num_subplots: int):
    row_size = int(num_subplots**0.5)
    col_size = num_subplots // row_size

    if num_subplots % row_size != 0:
        col_size += 1

    if col_size > 3:
        row_size += 1
        col_size = num_subplots // row_size
        if num_subplots % row_size != 0:
            col_size += 1

    return row_size, col_size


# %%


def plot_my_playlist(df: pd.DataFrame, plt_title: str = "Name not given") -> None:
    settings = import_settings()["models"]
    default_input_index_score = settings["common_text_score"]["input"][
        "default_input_index_score"
    ]

    audio_features = sorted(sc.get_audio_features())
    row_size, col_size = calculate_grid_size(
        len(audio_features) + 1
    )  # Plus one for the line plot

    df = df.sort_values("cum_duration")
    xs = df["cum_duration"]

    # Replace NaN with -2
    color = df["mood_mvmt"].fillna(-2)
    # Replace NaN with 0. Replace the input_track, which is by default 1000, to 0
    line1 = df["word_match_score"].replace(default_input_index_score, 0).fillna(0)
    # Replace NaN with the max value + 1
    replace_na_nn_index = int(max(df["nn_index_position"]) + 1)
    # Flip the value so that the higher the values, the lower it shows in the line
    line2 = -df["nn_index_position"].fillna(replace_na_nn_index)

    # https://254-online.com/colours-and-the-moods-they-invoke/
    color_map = {
        "first track": rgb_to_hex((4, 106, 56)),
        "brighten mood": rgb_to_hex((200, 16, 46)),
        "darken mood": rgb_to_hex((113, 178, 201)),
        "same mood": rgb_to_hex((173, 220, 145)),
        "random mood from random track": rgb_to_hex((95, 37, 159)),
        "nearest neighbor index position": rgb_to_hex((21, 71, 52)),
        "word match score": rgb_to_hex((213, 120, 0)),
    }

    # Set up subplots
    fig = go.Figure()
    specs = [[{"secondary_y": True} for _ in range(col_size)] for _ in range(row_size)]

    fig = make_subplots(
        rows=row_size,
        cols=col_size,
        shared_xaxes=True,
        horizontal_spacing=0.03,
        vertical_spacing=0.2,
        subplot_titles=audio_features,
        specs=specs,
    )

    # Loop
    row_i = 1
    col_i = 1
    for idx, feature in enumerate(audio_features):
        ys = df[feature]

        hover_text = df.apply(
            lambda row: f"Track: {row['track_name']}<br>Artist: {row['artist']}<br>Artist Genres: {row['artist_genres']}<br>Key: {row['translated_key']}<br>Energy: {row['translated_energy']}<br>Mood: {row['translated_mood']}",
            axis=1,
        )

        color_map_mood = {
            -1: color_map["darken mood"],
            1: color_map["brighten mood"],
            0: color_map["same mood"],
            -2: color_map["random mood from random track"],
        }
        # Make the first bar color grey and the rest based on the mood
        bar_colors = [
            color_map["first track"] if idx == 0 else color_map_mood[val]
            for idx, val in enumerate(color)
        ]

        # width = [xs[idx + 1] - xs[idx] for idx in range(len(xs) - 1)] + [
        #     xs.iloc[-1] * 0.5 - xs.iloc[-2] * 0.5
        # ]

        width = 1

        # Loop Bar Plot
        fig.add_trace(
            go.Bar(
                x=xs,
                y=ys,
                marker_color=bar_colors,
                width=width,
                hovertext=hover_text,
                hoverinfo="text",
                showlegend=False,
            ),
            row=row_i,
            col=col_i,
            secondary_y=False,
        )

        # Line Plot
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=line1,
                hovertext=hover_text,
                mode="lines+markers",
                line=dict(color=color_map["word match score"]),
                showlegend=False,
            ),
            row=row_size,
            col=col_size,
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=line2,
                hovertext=hover_text,
                mode="lines+markers",
                line=dict(color=color_map["nearest neighbor index position"]),
                showlegend=False,
            ),
            row=row_size,
            col=col_size,
            secondary_y=True,
        )

        # Axis Labels
        fig.update_xaxes(
            showticklabels=True,
            tickmode="linear",
            dtick=5,
            row=row_i,
            col=col_i,
            tickfont=dict(size=10),
        )
        fig.update_xaxes(
            tickmode="linear",
            dtick=5,
            row=row_size,
            col=col_size,
            tickfont=dict(size=10),
        )

        col_i += 1
        if col_i > 3:
            col_i = 1
            row_i += 1

    # Legend
    for legend_name, color in color_map.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, color=color),
                showlegend=True,
                name=legend_name,
            ),
            row=row_size,
            col=col_size,
        )

    # Title
    fig.update_layout(
        title={
            "text": f"Playlist '{plt_title}' analysis",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "bottom",
        },
        legend={
            "y": 0.5,
            "x": 1.17,
            "xanchor": "right",
            "yanchor": "middle",
            "title": "Color Map",
            "font": dict(size=12),
        },
        autosize=True,
    )
    # Whole plot x axis
    fig.update_layout(
        annotations=list(fig["layout"]["annotations"])  # type: ignore
        + [
            dict(
                x=0.5,
                y=-0.2,
                showarrow=False,
                text="Playlist Length (minutes)",
                xref="paper",
                yref="paper",
                font=dict(size=14),
            )
        ]
    )

    fig.show()


# %%
# https://www.geeksforgeeks.org/generating-word-cloud-python/


def wordcloud_plot(df_plt: pd.Series):
    from wordcloud import WordCloud, STOPWORDS

    comment_words = ""
    stopwords = set(STOPWORDS)

    for val in df_plt:
        val = str(val)
        tokens = val.split()
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        comment_words += " ".join(tokens) + " "

    wordcloud = WordCloud(
        width=800,
        height=800,
        background_color="white",
        stopwords=stopwords,
        min_font_size=10,
    ).generate(comment_words)

    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)

    return plt
