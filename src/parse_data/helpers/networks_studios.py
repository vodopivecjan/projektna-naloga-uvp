import pandas as pd
import ast
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"


def safe_literal_eval(x):
    if pd.isna(x):
        return []
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return []


def plot_networks_studios(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Spremeni string seznama v dejanski seznam
    df["trakt_networks"] = df["trakt_networks"].apply(safe_literal_eval)
    df["trakt_studios"] = df["trakt_studios"].apply(safe_literal_eval)

    # Razširi stolpce s kanali in produkcijskimi hišami, da dobimo po eno vrstico na posamezen element
    networks_exploded = df.explode("trakt_networks")
    studios_exploded = df.explode("trakt_studios")

    # Preštej, kolikokrat se pojavi vsak kanal in produkcijska hiša
    freq_networks = networks_exploded["trakt_networks"].value_counts()
    freq_studios = studios_exploded["trakt_studios"].value_counts()

    # ## Graf 1 - kanali
    plt.figure(figsize=(15, 6))
    freq_networks.head(20).plot(kind="bar")
    plt.xlabel("")
    plt.ylabel("Pogostost")
    plt.title("Top 20 medijskih kanalov po pogostosti")

    # ## Graf 2 - produkcijske hiše
    plt.figure(figsize=(15, 6))
    freq_studios.head(20).plot(kind="bar")
    plt.xlabel("")
    plt.ylabel("Pogostost")
    plt.title("Top 20 produkcijskih hiš po pogostosti")


    def prepare_pie_data(freq_series):
        total = freq_series.sum()
        # Delež vsake kategorije
        percent = freq_series / total * 100
        # Kategorije < 1 % združi v 'Ostalo'
        large = percent[percent >= 1]
        small = percent[percent < 1]
        others_sum = small.sum()
        # Združi nazaj v serijo za tortni prikaz
        final = large.copy()
        if others_sum > 0:
            final["Ostalo (< 1 %)"] = others_sum
        return final

    pie_networks = prepare_pie_data(freq_networks)
    pie_studios = prepare_pie_data(freq_studios)

    # Izris tortnih prikazov
    fig, axs = plt.subplots(1, 2, figsize=(18, 10))

    axs[0].pie(
        pie_networks, labels=pie_networks.index, autopct="%1.1f%%", startangle=140
    )
    axs[0].set_title("Delež medijskih kanalov")

    axs[1].pie(pie_studios, labels=pie_studios.index, autopct="%1.1f%%", startangle=140)
    axs[1].set_title("Delež produkcijskih hiš")

    plt.tight_layout()
    plt.show()
