import numpy as np
import pandas as pd
import plotly.express as px
from collections import OrderedDict


def compare_runtime_votes_ratings_normalized_axis(df):
    df = df.copy()

    # Pretvori čas trajanja iz stringa v število (če vsebuje "N.A." ali vejice)
    def pretvori_minute(x):
        if isinstance(x, str) and x.strip() == "N.A.":
            return np.nan
        return pd.to_numeric(str(x).replace(",", ""), errors="coerce")

    df["trakt_full_runtime_min"] = df["trakt_full_runtime_min"].apply(pretvori_minute)
    df["trakt_vote_count_imdb"] = df["trakt_vote_count_imdb"].apply(pretvori_minute)
    df["trakt_rating_imdb"] = pd.to_numeric(df["trakt_rating_imdb"], errors="coerce")

    # Odstrani vrstice s praznimi vrednostmi
    df = df.dropna(
        subset=["trakt_full_runtime_min", "trakt_vote_count_imdb", "trakt_rating_imdb"]
    )

    # Odstrani res dolge šove (1% najdlje trajajoči), ker če ne,
    # se na normaliziranem traku čisto preveč raztegne
    runtime_99 = df["trakt_full_runtime_min"].quantile(0.99)
    df = df[df["trakt_full_runtime_min"] <= runtime_99]

    # Pretvori čas iz minut v ure
    df["trajanje_ure"] = df["trakt_full_runtime_min"] / 60

    # Popup formatted
    df["trajanje_ure_1dec"] = df["trajanje_ure"].round(1).astype(str) + "h"

    # Nariši graf z uporabo Plotly
    fig = px.scatter(
        df,
        x="trajanje_ure",
        y="trakt_vote_count_imdb",
        color="trakt_rating_imdb",
        hover_name="imdb_title",  # Naslov serije ob lebdenju
        hover_data={
            "trajanje_ure_1dec": True,
            "trakt_vote_count_imdb": True,
            "trajanje_ure": False,
        },
        labels={
            "trakt_vote_count_imdb": "Število glasov",
            "trajanje_ure_1dec": "Skupni čas trajanja (ure)",
            "trakt_rating_imdb": "IMDB ocena",
        },
        color_continuous_scale="viridis",
        title="Primerjava trajanja, števila glasov in IMDB ocen (linearno normalizirane osi)",
    )

    fig.update_layout(width=1600, height=800)

    fig.show()


def compare_runtime_votes_ratings_non_normalized_axis(df):
    from collections import OrderedDict

    df = df.copy()

    def pretvori_minute(x):
        if isinstance(x, str) and x.strip() == "N.A.":
            return np.nan
        return pd.to_numeric(str(x).replace(",", ""), errors="coerce")

    df["trakt_full_runtime_min"] = df["trakt_full_runtime_min"].apply(pretvori_minute)
    df["trakt_vote_count_imdb"] = df["trakt_vote_count_imdb"].apply(pretvori_minute)
    df["trakt_rating_imdb"] = pd.to_numeric(df["trakt_rating_imdb"], errors="coerce")

    df = df.dropna(
        subset=["trakt_full_runtime_min", "trakt_vote_count_imdb", "trakt_rating_imdb"]
    )

    df["trajanje_ure"] = df["trakt_full_runtime_min"] / 60

    # Log1p transform, slightly stretched on X
    df["vote_log"] = np.log1p(df["trakt_vote_count_imdb"])
    df["runtime_log"] = np.log1p(df["trajanje_ure"]) * 1.2  # less compression on left

    # Popup formatted
    df["trajanje_ure_1dec"] = df["trajanje_ure"].round(1).astype(str) + "h"

    def format_votes(v):
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        elif v >= 1_000:
            return f"{v / 1_000:.1f}k"
        else:
            return str(int(v))

    df["vote_count_formatted"] = df["trakt_vote_count_imdb"].apply(format_votes)

    fig = px.scatter(
        df,
        x="runtime_log",
        y="vote_log",
        color="trakt_rating_imdb",
        hover_name="imdb_title",
        hover_data=OrderedDict(
            [
                ("vote_count_formatted", True),
                ("trajanje_ure_1dec", True),
                ("trakt_rating_imdb", True),
                ("trajanje_ure", False),
                ("trakt_vote_count_imdb", False),
                ("runtime_log", False),
                ("vote_log", False),
            ]
        ),
        labels={
            "trajanje_ure_1dec": "Trajanje (ure)",
            "vote_count_formatted": "Št. glasov",
            "trakt_rating_imdb": "IMDB ocena",
        },
        color_continuous_scale="viridis",
        title="Trajanje, število glasov in IMDB ocena (raztegnjeni deli z največ podatki za boljšo berljivost)",
    )

    # Y-axis ticks
    # fmt: off
    vote_ticks = [0, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, 2_000_000, 3_000_000]
    # fmt: on
    vote_tick_vals = np.log1p(vote_ticks)
    vote_tick_labels = [
        f"{v // 1_000_000}M" if v >= 1_000_000 else f"{int(v / 1000)}k"
        for v in vote_ticks
    ]

    # X-axis ticks
    max_hours = df["trajanje_ure"].max()
    runtime_ticks = [0, 5, 10, 20, 50, 100, 200, 500, 1000]
    runtime_ticks = [x for x in runtime_ticks if x <= max_hours + 10]
    runtime_tick_vals = np.log1p(runtime_ticks) * 1.2
    runtime_tick_labels = [f"{v}h" for v in runtime_ticks]

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=runtime_tick_vals,
            ticktext=runtime_tick_labels,
            title="Skupni čas trajanja (ure)",
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=vote_tick_vals,
            ticktext=vote_tick_labels,
            title="Število glasov (v tisočicah ali milijonih)",
        ),
        xaxis_tickangle=0,  # keep x labels horizontal
        width=1600,
        height=800,
    )

    fig.show()


def compare_avg_ep_runtime_votes_ratings_normalized_axis(df):
    df = df.copy()

    # Pretvori čas trajanja iz stringa v število (če vsebuje "N.A." ali vejice)
    def pretvori_minute(x):
        if isinstance(x, str) and x.strip() == "N.A.":
            return np.nan
        return pd.to_numeric(str(x).replace(",", ""), errors="coerce")

    df["trakt_avg_ep_runtime_min"] = df["trakt_avg_ep_runtime_min"].apply(pretvori_minute)
    df["trakt_vote_count_imdb"] = df["trakt_vote_count_imdb"].apply(pretvori_minute)
    df["trakt_rating_imdb"] = pd.to_numeric(df["trakt_rating_imdb"], errors="coerce")

    # Odstrani vrstice s praznimi vrednostmi
    df = df.dropna(
        subset=["trakt_avg_ep_runtime_min", "trakt_vote_count_imdb", "trakt_rating_imdb"]
    )

    # Odstrani res dolge šove (1% najdlje trajajoči), ker če ne,
    # se na normaliziranem traku čisto preveč raztegne
    runtime_99 = df["trakt_avg_ep_runtime_min"].quantile(0.99)
    df = df[df["trakt_avg_ep_runtime_min"] <= runtime_99]


    # Nariši graf z uporabo Plotly
    fig = px.scatter(
        df,
        x="trakt_avg_ep_runtime_min",
        y="trakt_vote_count_imdb",
        color="trakt_rating_imdb",
        hover_name="imdb_title",  # Naslov serije ob lebdenju
        hover_data={
            "trakt_avg_ep_runtime_min": True,
            "trakt_vote_count_imdb": True,
            "trakt_rating_imdb": True,
        },
        labels={
            "trakt_vote_count_imdb": "Število glasov",
            "trakt_avg_ep_runtime_min": "Povpreči čas trajanja epizode (minute)",
            "trakt_rating_imdb": "IMDB ocena",
        },
        color_continuous_scale="viridis",
        title="Primerjava povprečnega trajanja dolžine epizode, števila glasov in IMDB ocen (linearno normalizirane osi)",
    )

    fig.update_layout(width=1600, height=800)

    fig.show()