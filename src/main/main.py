# import os
import time
import csv


from main.debug import execute_and_time, pp


from main.vars import FIELDNAMES
from main.scraping.scrape_imdb import scrape_imdb_top_tv
from main.scraping.scrape_trakt import scrape_trakt_from_top_tv_data
from main.scraping.scrape_wiki import find_scrape_wikipedia
from main.cache.cache import save_cache, load_cache


def get_top_shows_and_data_then_save_to_csv():
    
    # top_tv_imdb_data = execute_and_time(scrape_imdb_top_tv)
    # save_cache("imdb_data_top_tv", top_tv_imdb_data)

    imdb_data_top_tv = load_cache("imdb_data_top_tv")
    # pp(imdb_data_top_tv)

    data =  execute_and_time(scrape_trakt_from_top_tv_data, imdb_data_top_tv)
    save_cache("full_data", data)
    pp(data)

    # # Save to CSV
    # with open("../output/top_tv_shows.csv", "w", newline="", encoding="utf-8") as f:
    #     writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    #     writer.writeheader()
    #     writer.writerows(top_tv_data)


def get_wiki_pages():
    with open("../output/top_tv_shows.csv", newline="", encoding="utf-8") as csvfile:
        data = list(csv.DictReader(csvfile))

    for row in data:
        find_scrape_wikipedia(row)


def main():
    get_top_shows_and_data_then_save_to_csv()
    # get_wiki_pages()

    # # print(os.getcwd())
