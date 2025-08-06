import requests

from bs4 import BeautifulSoup

# from main.debug import pp

from main.vars import BROWSER_LIKE_HEADERS


def scrape_wikipedia_page(series_data):
    part_url = series_data["trakt_wiki_link"]
    url = f"https://trakt.tv/{part_url}"
    res = requests.get(url, headers=BROWSER_LIKE_HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    # Find the infobox
    infobox = soup.select_one("table.infobox.vevent")

    # Extract rows
    rows = infobox.find_all("tr")

    desired_keys = {
        "wiki_created_by": ["Created by"],
        "wiki_written_by": ["Written by"],
        "wiki_executive_producers": ["Executive producers", "Executive producer"],
        "wiki_producers": ["Producers", "Producer"],
        "wiki_cinematography": ["Cinematography"],
        "wiki_editors": ["Editors", "Editor"],
    }

    # Flatten all variants into a single set for fast matching
    all_variants = set(k for variants in desired_keys.values() for k in variants)

    data = {}
    for row in rows:
        header = row.find("th")
        value = row.find("td")
        if header and value:
            key_text = header.get_text(" ", strip=True)
            if key_text in all_variants:
                # If the value contains a <ul>, extract list items
                ul = value.find("ul")
                if ul:
                    items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
                    data[key_text] = items
                else:
                    # Otherwise, fallback to comma-splitting
                    raw = value.get_text(" ", strip=True)
                    items = [item.strip() for item in raw.split(",") if item.strip()]
                    data[key_text] = items

    # Utility: Get first matching key from variants
    def get_value(data, variants):
        for k in variants:
            if k in data:
                return data[k]
        return "N.A."

    formatted_data = {
        "wiki_created_by": get_value(data, desired_keys["wiki_created_by"]),
        "wiki_written_by": get_value(data, desired_keys["wiki_written_by"]),
        "wiki_executive_producers": get_value(
            data, desired_keys["wiki_executive_producers"]
        ),
        "wiki_producers": get_value(data, desired_keys["wiki_producers"]),
        "wiki_cinematography": get_value(data, desired_keys["wiki_cinematography"]),
        "wiki_editors": get_value(data, desired_keys["wiki_editors"]),
    }

    if formatted_data.get("wiki_written_by") is not None:
        print(f"wiki_written_by found in wiki of {series_data['imdb_title']}.")

    return formatted_data


def scrape_wiki_from_data_imdb_trakt(data_imdb_trakt):
    data = []

    for i, series_data in enumerate(data_imdb_trakt):
        if i > 5:
            # ## DEMO
            # return data
            pass

        imdb_title = series_data["imdb_title"]
        try:
            print(f"Started scraping Wikipedia for IMDB title: {imdb_title}")
            wiki_data = scrape_wikipedia_page(series_data)
            series_data.update(wiki_data)
            data.append(series_data)
        except Exception:
            print(
                f"\nError: Something went wrong when scraping Wikipedia page for title {imdb_title}.\n"
            )
            raise

    return data
