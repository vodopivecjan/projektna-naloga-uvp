import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scrape_imdb_top_tv():
    url = "https://www.imdb.com/chart/toptv/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        # need this for the language to be english
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # IMDb has a <ul> of TV show items
    ul = soup.select_one("ul.ipc-metadata-list")  # or use the full path if needed
    if not ul:
        # TODO ERROR HANDLING
        print("List not found")
        return []

    shows = []
    for i, li in enumerate(ul.find_all("li", recursive=False), start=1):
        entry = {}

        title = li.select_one("h3.ipc-title__text").text
        # split the rank from title
        title = title.removeprefix(f"{i}. ") if title else None
        entry["title"] = title

        entry["rank"] = i

        # url
        link_tag = li.select_one("a.ipc-title-link-wrapper")
        link = link_tag["href"] if link_tag and "href" in link_tag.attrs else None
        parsed = urlparse(link)
        entry["link"] = parsed.path

        # metadata spans
        metadata_spans = li.select(".cli-title-metadata span")

        ## years
        years_text = metadata_spans[0].text if len(metadata_spans) > 0 else None
        years_text = years_text.replace("\u2013", "-")

        entry["ongoing"] = "No"
        if "-" in years_text:
            # show is finished or ongoing
            years_list = years_text.split("-", 1)
            entry["year_start"] = years_list[0].strip()
            year_end = years_list[1].strip()

            if not year_end:
                entry["year_end"] = None
                entry["ongoing"] = "Yes"
            else:
                entry["year_end"] = year_end
        else:
            # the show ran for 1 year
            entry["year_start"] = years_text
            entry["year_end"] = years_text

        ## number of episodes
        num_of_episodes = metadata_spans[1].text if len(metadata_spans) > 1 else None
        entry["num_of_episodes"] = num_of_episodes.removesuffix(" eps")

        ## parental ranting
        entry["parental_rating"] = (
            metadata_spans[2].text if len(metadata_spans) > 2 else None
        )

        ## series type
        entry["series_type"] = (
            metadata_spans[3].text if len(metadata_spans) > 3 else None
        )

        # user rating
        user_rating_tag = li.select_one("span.ipc-rating-star--rating")
        entry["user_rating"] = user_rating_tag.text.strip() if user_rating_tag else None

        # count of user ratings
        votes_tag = li.select_one("span.ipc-rating-star--voteCount")
        user_votes_count = votes_tag.text if votes_tag else None
        start = user_votes_count.find("(")
        end = user_votes_count.find(")", start)
        if start != -1 and end != -1:
            entry["user_votes_count"] = user_votes_count[start + 1 : end]
        else:
            entry["user_votes_count"] = None

        shows.append(entry)

    return shows
