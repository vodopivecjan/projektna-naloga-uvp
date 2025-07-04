# import os
import csv


from main.vars import FIELDNAMES
from main.scraping.scrape import scrape_imdb_top_tv


def main():
    top_tv = scrape_imdb_top_tv()

    # print(os.getcwd())

    # Save to CSV
    with open("../output/top_tv_shows.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(top_tv)

    # for show in top_tv[:5]:
    #     print(
    #         f"{show['rank']}. {show['title']} ({show['year']}) - {show['rating']} - {show['url']}"
    #     )
