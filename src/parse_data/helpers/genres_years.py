import pandas as pd
import ast
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "DejaVu Sans"


def plot_genres_years(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Odstrani manjkajoče vrednosti
    df = df.dropna(subset=["imdb_year_start", "trakt_genres"])
    df["imdb_year_start"] = pd.to_numeric(df["imdb_year_start"], errors="coerce")
    df["imdb_year_end"] = pd.to_numeric(df["imdb_year_end"], errors="coerce")

    # Če manjka imdb_year_end in je ongoing, uporabimo trenutno leto
    df.loc[
        df["imdb_year_end"].isna() & (df["imdb_ongoing"] == "Yes"), "imdb_year_end"
    ] = pd.Timestamp.now().year

    # Pretvori string v seznam žanrov
    def parse_genres(val):
        try:
            return ast.literal_eval(val)
        except Exception:
            return []

    df["genres_list"] = df["trakt_genres"].apply(parse_genres)

    # Razširi po letih, ko je bila serija aktivna
    rows = []
    for _, row in df.iterrows():
        start = int(row["imdb_year_start"])
        end = int(row["imdb_year_end"]) if not pd.isna(row["imdb_year_end"]) else start
        for leto in range(start, end + 1):
            for zanr in row["genres_list"]:
                rows.append({"leto": leto, "žanr": zanr})

    df_letni_zanri = pd.DataFrame(rows)

    # Preštej pojavitve žanrov po letih
    tabela = df_letni_zanri.groupby(["leto", "žanr"]).size().unstack(fill_value=0)

    # Obdrži samo top 10 žanrov po skupni vsoti
    top_zanri = tabela.sum().sort_values(ascending=False).head(10).index
    tabela = tabela[top_zanri]

    # Nariši stacked bar chart (naloženi stolpični diagram :))
    tabela.plot(kind="bar", stacked=True, figsize=(16, 8))
    plt.xlabel("Leto")
    plt.ylabel("Število serij po žanrih (ena serija se lahko v stolpcu šteje večkrat)")
    plt.title("Žanri po letih (seštevek vseh aktivnih serij tisti leto)")
    plt.legend(title="Žanr")
    plt.tight_layout()
    plt.show()
