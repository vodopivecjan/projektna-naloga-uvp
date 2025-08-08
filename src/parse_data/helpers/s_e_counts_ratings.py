import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"

def plot_rating_episodes_seasons_counts(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Pretvori stolpce v numerične vrednosti
    df["trakt_rating_imdb"] = pd.to_numeric(df["trakt_rating_imdb"], errors="coerce")
    df["trakt_num_of_episodes"] = pd.to_numeric(df["trakt_num_of_episodes"], errors="coerce")
    df["trakt_num_of_seasons"] = pd.to_numeric(df["trakt_num_of_seasons"], errors="coerce")

    # Odstrani vrstice z manjkajočimi vrednostmi
    df = df.dropna(subset=["trakt_rating_imdb", "trakt_num_of_episodes", "trakt_num_of_seasons"])

    # Ustvari graf: ocena glede na število epizod
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=df, x="trakt_num_of_episodes", y="trakt_rating_imdb", alpha=0.7)
    plt.xlabel("Število epizod")
    plt.ylabel("IMDB ocena")
    plt.title("IMDB ocena glede na število epizod")

    # Ustvari graf: ocena glede na število sezon
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x="trakt_num_of_seasons", y="trakt_rating_imdb", alpha=0.7)
    plt.xlabel("Število sezon")
    plt.ylabel("IMDB ocena")
    plt.title("IMDB ocena glede na število sezon")

    # Prikaži grafa
    plt.tight_layout()
    plt.show()


def plot_vote_count_episodes_seasons_counts(df: pd.DataFrame):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Pretvori stolpce v numerične vrednosti
    df["trakt_vote_count_imdb"] = pd.to_numeric(df["trakt_vote_count_imdb"].astype(str).str.replace(",", ""), errors="coerce")
    df["trakt_num_of_episodes"] = pd.to_numeric(df["trakt_num_of_episodes"], errors="coerce")
    df["trakt_num_of_seasons"] = pd.to_numeric(df["trakt_num_of_seasons"], errors="coerce")

    # Odstrani vrstice z manjkajočimi vrednostmi
    df = df.dropna(subset=["trakt_vote_count_imdb", "trakt_num_of_episodes", "trakt_num_of_seasons"])

    # Ustvari graf: glasovi glede na število epizod
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    sns.scatterplot(data=df, x="trakt_num_of_episodes", y="trakt_vote_count_imdb", alpha=0.7)
    plt.xlabel("Število epizod")
    plt.ylabel("Število glasov (IMDB)")
    plt.title("Število glasov glede na število epizod")

    # Ustvari graf: glasovi glede na število sezon
    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x="trakt_num_of_seasons", y="trakt_vote_count_imdb", alpha=0.7)
    plt.xlabel("Število sezon")
    plt.ylabel("Število glasov (IMDB)")
    plt.title("Število glasov glede na število sezon")

    # Prikaži grafa
    plt.tight_layout()
    plt.show()
