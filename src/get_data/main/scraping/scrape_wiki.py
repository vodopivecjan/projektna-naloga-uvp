import re
import requests

from bs4 import BeautifulSoup

# from main.debug import pp

from main.vars import BROWSER_LIKE_HEADERS

from main.scraping.scraping_shared import for_loop_scrape_logic


def scrape_wikipedia_page(series_data, iteration):
    # ## BACKUP IF NO WIKIPEDIA PAGE IS FOUND OR MISSING DATA
    default_wiki_data = {
        "wiki_created_by": "N.A.",
        "wiki_written_by": "N.A.",
        "wiki_executive_producers": "N.A.",
        "wiki_producers": "N.A.",
        "wiki_cinematography": "N.A.",
        "wiki_editors": "N.A.",
    }

    # Validate Trakt wiki link
    try:
        part_url = series_data["trakt_wiki_link"]
    except KeyError:
        print(
            "\nError: Missing required key: 'trakt_wiki_link'\n"
            "Make sure to run the Trakt scraping before attempting Wikipedia scraping.\n"
        )
        raise

    url = f"https://trakt.tv/{part_url}"
    res = requests.get(url, headers=BROWSER_LIKE_HEADERS)

    # Check if redirected to Wikipedia
    if "en.wikipedia.org" not in res.url:
        return default_wiki_data

    soup = BeautifulSoup(res.text, "html.parser")
    infobox = soup.select_one("table.infobox.vevent") or soup.select_one(
        "table.infobox"
    )
    if not infobox:
        return default_wiki_data

    rows = infobox.find_all("tr")

    desired_keys = {
        "wiki_created_by": ["Created by"],
        "wiki_written_by": ["Written by"],
        "wiki_executive_producers": ["Executive producers", "Executive producer"],
        "wiki_producers": ["Producers", "Producer"],
        "wiki_cinematography": ["Cinematography"],
        "wiki_editors": ["Editors", "Editor"],
    }

    all_variants = set(k for variants in desired_keys.values() for k in variants)
    extracted = {}

    for row in rows:
        header = row.find("th")
        value = row.find("td")
        if header and value:
            key_text = header.get_text(" ", strip=True)
            if key_text in all_variants:
                ul = value.find("ul")
                if ul:
                    items = [li.get_text(" ", strip=True) for li in ul.find_all("li")]
                else:
                    raw = value.get_text(" ", strip=True)
                    items = [item.strip() for item in raw.split(",") if item.strip()]
                extracted[key_text] = items

    def clean_entry(text: str) -> str:
        text = re.sub(r"\[[^\]]*\]", "", text)  # Remove [ ... ]
        text = re.sub(r"\([^\)]*\)", "", text)  # Remove ( ... )
        text = text.replace("\u0131", "i")  # Replace Turkish dotless 'ı' (U+0131)
        return text.strip()

    def resolve_field(variants):
        for v in variants:
            if v in extracted:
                cleaned = [clean_entry(item) for item in extracted[v]]
                return [item for item in cleaned if item] or "N.A."
        return "N.A."

    wiki_data = {key: resolve_field(variants) for key, variants in desired_keys.items()}

    return wiki_data


def scrape_wikipedia_from_data_imdb_trakt(data):
    id_whitelist = []
    # id_whitelist = ["tt12392504"]
    return for_loop_scrape_logic(
        "wiki", scrape_wikipedia_page, data, id_whitelist=id_whitelist
    )
