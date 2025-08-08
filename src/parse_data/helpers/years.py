import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "DejaVu Sans"


def plot_active_series_years(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Pretvori stolpca z leti v številske vrednosti (uporabi 'coerce' za napačne vrednosti)
    df["imdb_year_start"] = pd.to_numeric(df["imdb_year_start"], errors="coerce")
    df["imdb_year_end"] = pd.to_numeric(df["imdb_year_end"], errors="coerce")

    # Za manjkajoče vrednosti v 'imdb_year_end' nastavi trenutno leto (pomeni, da še poteka, isto kot imdb_ongoing)
    current_year = pd.Timestamp.now().year
    df["imdb_year_end"] = df["imdb_year_end"].fillna(current_year)

    # Ustvari seznam vseh let, v katerih je bila serija aktivna
    active_years = []

    for _, vrstica in df.iterrows():
        start = int(vrstica["imdb_year_start"])
        end = int(vrstica["imdb_year_end"])
        active_years.extend(range(start, end + 1))

    # Preštej število serij, ki so bile aktivne v posameznem letu
    number_of_active = pd.Series(active_years).value_counts().sort_index()

    # Prikaži graf
    plt.figure(figsize=(15, 6))
    number_of_active.plot(kind="bar", width=0.7)
    plt.xlabel("Leto")
    plt.ylabel("Število aktivnih serij")
    plt.title("Število aktivnih serij po posameznem letu")
    plt.tight_layout()
    plt.show()
