import json
import csv


from main.debug import execute_and_time, pp  # noqa: F401

from main.cache.cache import save_cache, load_cache, delete_cache_from_list_no_error

from main.vars import OUTPUT_FOLDER_PATH, CACHE_NAMES_SORTED


from main.scraping.scrape_imdb import scrape_imdb_toptv
from main.scraping.scrape_trakt import scrape_trakt_from_data_imdb
from main.scraping.scrape_wiki import scrape_wikipedia_from_data_imdb_trakt


def get_biggest_stored_dataset():
    for name in CACHE_NAMES_SORTED:
        try:
            return load_cache(name)
        except FileNotFoundError:
            continue
    return []


def get_full_data_from_toptv_shows(fresh=False):
    if fresh:
        delete_cache_from_list_no_error(CACHE_NAMES_SORTED)

    # ## Scrape IMDB
    data = get_biggest_stored_dataset()
    data_imdb = execute_and_time(scrape_imdb_toptv, data)
    save_cache("data_imdb", data_imdb)

    # ## Scrape Trakt
    data = get_biggest_stored_dataset()
    data_imdb_trakt = execute_and_time(scrape_trakt_from_data_imdb, data)
    save_cache("data_imdb_trakt", data_imdb_trakt)

    # ## Scrape Wikipedia
    data = get_biggest_stored_dataset()
    data_imdb_trakt_wiki = execute_and_time(scrape_wikipedia_from_data_imdb_trakt, data)
    save_cache("data_imdb_trakt_wiki", data_imdb_trakt_wiki)

    # ## GET FINAL DATA
    final_data = get_biggest_stored_dataset()

    return final_data


def main():
    full_data = get_full_data_from_toptv_shows(fresh=True)
    # full_data = get_full_data_from_toptv_shows()

    # ## Write FULL DATA to JSON file
    json_output_file = OUTPUT_FOLDER_PATH / "toptv_shows_full_data.json"
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)

    # ## Write ONLY DATA TO BE PARSED to CSV file
    FULL_DATA_KEYS_TO_REMOVE = ["imdb_id", "trakt_title", "trakt_wiki_link"]

    # strip the unecessary data used for debugging/acquiring data
    for d in full_data:
        for key in FULL_DATA_KEYS_TO_REMOVE:
            if key in d:
                d.pop(key, None)

    csv_output_file = OUTPUT_FOLDER_PATH / "toptv_shows_full_data.csv"
    with open(csv_output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=full_data[0].keys())
        writer.writeheader()
        writer.writerows(full_data)
