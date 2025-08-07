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

    # ## CHECK IF THE PAGE CAN BE SCRAPED
    try:
        part_url = series_data["trakt_wiki_link"]
    except KeyError:
        print(
            "\nError: Missing required key: 'trakt_wiki_link'\n"
            "This key is required when scraping Wikipedia.\n"
            "This likely means the Trakt data has not been scraped yet.\n"
            "Make sure to run the Trakt scraping before attempting Trakt Wikipedia.\n"
        )
        raise

    url = f"https://trakt.tv/{part_url}"

    res = requests.get(url, headers=BROWSER_LIKE_HEADERS)

    # ## ensure that the current page is wikipedia
    # ## and if it isnt then follow html redirects
    # ## until it is or the max_hops is reached
    if "en.wikipedia.org" not in res.url:
        # no wikipedia page found so just return default data
        return default_wiki_data

    soup = BeautifulSoup(res.text, "html.parser")

    # Find the infobox
    infobox = soup.select_one("table.infobox.vevent")
    if not infobox:
        infobox = soup.select_one("table.infobox")
    if not infobox:
        return default_wiki_data

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

    return formatted_data


def scrape_wikipedia_from_data_imdb_trakt(data):
    # id_whitelist = ["tt12392504"]
    id_whitelist = []
    # id_blacklist = []
    return for_loop_scrape_logic(
        "wiki", scrape_wikipedia_page, data, id_whitelist=id_whitelist
    )
