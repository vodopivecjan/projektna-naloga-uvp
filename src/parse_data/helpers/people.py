import ast
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
from collections import defaultdict, Counter

def plot_involved_people(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    # Pomožna funkcija za pretvorbo iz str v seznam
    def parse_list(x):
        if isinstance(x, str):
            try:
                return set(ast.literal_eval(x))
            except Exception:
                return set()
        return set()

    # Skupine sodelujočih
    igralci = set()
    ustvarjalci = set()
    produkcija = set()

    for _, row in df.iterrows():
        # Igralci
        igralci |= parse_list(row.get("trakt_series_regulars", ""))
        igralci |= parse_list(row.get("trakt_guest_stars", ""))

        # Ustvarjalci
        ustvarjalci |= parse_list(row.get("wiki_created_by", ""))
        ustvarjalci |= parse_list(row.get("wiki_written_by", ""))

        # Produkcija
        produkcija |= parse_list(row.get("wiki_producers", ""))
        produkcija |= parse_list(row.get("wiki_executive_producers", ""))
        produkcija |= parse_list(row.get("wiki_editors", ""))
        produkcija |= parse_list(row.get("wiki_cinematography", ""))

    # Vennov diagram
    plt.figure(figsize=(10, 8))
    venn3(
        [igralci, ustvarjalci, produkcija],
        set_labels=("Igralci", "Ustvarjalci", "Produkcija")
    )
    plt.title("Prekrivanje oseb po vlogah v produkciji serij")
    plt.show()


def plot_number_of_apperances_for_people_in_groups(df):
    # Naredi kopijo, da ne spreminjaš originala
    df = df.copy()

    def parse_list(x):
        if isinstance(x, str):
            try:
                return set(ast.literal_eval(x))
            except Exception:
                return set()
        return set()

    osebe_po_skupinah = {
        'igralci': defaultdict(set),
        'ustvarjalci': defaultdict(set),
        'produkcija': defaultdict(set)
    }

    for _, row in df.iterrows():
        title = row.get("imdb_title", "N.A.")

        igralci = parse_list(row.get("trakt_series_regulars", "")) | parse_list(row.get("trakt_guest_stars", ""))
        ustvarjalci = parse_list(row.get("wiki_created_by", "")) | parse_list(row.get("wiki_written_by", ""))
        produkcija = (
            parse_list(row.get("wiki_producers", ""))
            | parse_list(row.get("wiki_executive_producers", ""))
            | parse_list(row.get("wiki_editors", ""))
            | parse_list(row.get("wiki_cinematography", ""))
        )

        osebe_po_skupinah['igralci'][title] = igralci
        osebe_po_skupinah['ustvarjalci'][title] = ustvarjalci
        osebe_po_skupinah['produkcija'][title] = produkcija

    rezultati = {}
    for skupina, serije_dict in osebe_po_skupinah.items():
        counter = Counter()
        for title, imena in serije_dict.items():
            for ime in imena:
                counter[ime] += 1
        rezultati[skupina] = counter

    # Plot each group
    for skupina, counter in rezultati.items():
        top_30 = counter.most_common(30)
        osebe, stevila = zip(*top_30) if top_30 else ([], [])
        plt.figure(figsize=(11, 8))
        plt.barh(osebe, stevila)
        plt.title(f"Top 30 oseb v skupini '{skupina}' po številu različnih serij")
        plt.xlabel("Število serij")
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

