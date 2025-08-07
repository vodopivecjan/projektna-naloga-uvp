import pandas as pd
import matplotlib.pyplot as plt


def tabela_serije_miniserije_razmerje(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    shows_per_type = (
        df.groupby("imdb_series_type")
        .size()
        .reset_index(name="Št. serij")
        .sort_values(by="Št. serij", ascending=False)
    )

    shows_per_type = shows_per_type.rename(columns={"imdb_series_type": "Tip serije"})

    total_shows = shows_per_type["Št. serij"].sum()

    total_row = pd.DataFrame([{"Tip serije": "Vse skupaj", "Št. serij": total_shows}])

    # Združi vrstico "Vse skupaj" z ostalimi
    shows_per_type_with_total = pd.concat(
        [total_row, shows_per_type], ignore_index=True
    )

    # Izračunaj odstotke, ne da bi vključil vrstico "Vse skupaj" v izračun
    shows_per_type_with_total["% Serij"] = (
        shows_per_type_with_total["Št. serij"] / total_shows * 100
    ).fillna(0).astype(int).astype(str) + " %"

    return shows_per_type_with_total


def tabela_serije_miniserije_po_drzavah(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Skupno št. po državah
    shows_per_country = (
        df.groupby("trakt_country_of_origin").size().reset_index(name="Št. vseh serij")
    )
    # Število miniserij po državah
    miniseries = (
        df[df["imdb_series_type"] == "TV Mini Series"]
        .groupby("trakt_country_of_origin")
        .size()
        .reset_index(name="Miniserije")
    )
    # Število serij po državah
    series = (
        df[df["imdb_series_type"] == "TV Series"]
        .groupby("trakt_country_of_origin")
        .size()
        .reset_index(name="Serije")
    )

    # Združi vse
    shows_per_country = shows_per_country.merge(
        series, on="trakt_country_of_origin", how="left"
    ).merge(miniseries, on="trakt_country_of_origin", how="left")

    # Dodajmo še procentualno
    shows_per_country["% Serije"] = (
        shows_per_country["Serije"] / shows_per_country["Št. vseh serij"] * 100
    ).round(0).fillna(0).astype(int).astype(str) + " %"
    shows_per_country["% Miniserije"] = (
        shows_per_country["Miniserije"] / shows_per_country["Št. vseh serij"] * 100
    ).round(0).fillna(0).astype(int).astype(str) + " %"

    # Zamenjaj NaN z 0 in naj bodo vse integerji
    to_format = ["Miniserije", "Serije"]
    shows_per_country[to_format] = shows_per_country[to_format].fillna(0).astype(int)

    shows_per_country = shows_per_country.sort_values(
        by="trakt_country_of_origin", key=lambda col: col == "N.A."
    ).reset_index(drop=True)

    return shows_per_country.rename(
        columns={"trakt_country_of_origin": "Država izvora"}
    )


def plot_active_series(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Pretvori stolpca z leti v številske vrednosti (uporabi 'coerce' za napačne vrednosti)
    df['imdb_year_start'] = pd.to_numeric(df['imdb_year_start'], errors='coerce')
    df['imdb_year_end'] = pd.to_numeric(df['imdb_year_end'], errors='coerce')

    # Za manjkajoče vrednosti v 'imdb_year_end' nastavi trenutno leto (predpostavka, da serija še poteka)
    current_year =  pd.Timestamp.now().year
    df['imdb_year_end'] = df['imdb_year_end'].fillna(current_year)

    # Ustvari seznam vseh let, v katerih je bila serija aktivna
    active_years = []

    for _, vrstica in df.iterrows():
        start = int(vrstica['imdb_year_start'])
        end = int(vrstica['imdb_year_end'])
        active_years.extend(range(start, end + 1))

    # Preštej število serij, ki so bile aktivne v posameznem letu
    number_of_active = pd.Series(active_years).value_counts().sort_index()

    # Prikaži graf
    plt.figure(figsize=(15,6))
    number_of_active.plot(kind='bar', width=0.7)
    plt.xlabel('Leto')
    plt.ylabel('Število aktivnih serij')
    plt.title('Število aktivnih serij po posameznem letu')
    plt.tight_layout()
    plt.show()
