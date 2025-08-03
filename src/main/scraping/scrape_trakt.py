import requests

from bs4 import BeautifulSoup

from main.vars import BROWSER_LIKE_HEADERS


def scrape_trakt_page(series_data):
    imdb_id = series_data["imdb_id"]
    imdb_ongoing = series_data["imdb_ongoing"]

    url = f"https://trakt.tv/search/imdb/{imdb_id}"
    res = requests.get(url, headers=BROWSER_LIKE_HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    # # Title
    trakt_title = "N.A."
    title_tag = soup.select_one("div.container.summary h1")
    trakt_title = title_tag.text.strip()

    # # IMDB rating and Vote count
    trakt_rating_imdb = "N.A."
    trakt_vote_count_imdb = "N.A."
    li = soup.find("li", class_="imdb")
    if li:
        rating_div = li.find("div", class_="rating")
        if rating_div:
            trakt_rating_imdb = rating_div.get_text(strip=True)
        votes_div = li.find("div", class_="votes")
        if votes_div:
            span = votes_div.find("span")
            if span:
                trakt_vote_count_imdb = span.get_text(strip=True)

    # # Avg runtime
    trakt_avg_ep_runtime = "N.A."
    label = soup.find("label", string="Runtime")
    if label:
        span = label.find_next_sibling("span", class_="humanized-minutes")
        if span:
            trakt_avg_ep_runtime = span.get("data-full-minutes")

    # # Total runtime
    trakt_full_runtime = "N.A."
    label = soup.find("label", string="Total Runtime")
    if label:
        span = label.find_next_sibling("span", class_="humanized-minutes")
        if span:
            trakt_full_runtime = span.get("data-full-minutes")

    # # Network
    trakt_network = "N.A."
    if imdb_ongoing == "No":
        label = soup.find("label", string="Network")
        trakt_network = str(label.next_sibling).strip()
    if trakt_network == "N.A.":
        label = soup.find("label", string="Airs")
        if label:
            siblings = list(label.next_siblings)
            for sibling in reversed(siblings):
                if isinstance(sibling, str):
                    text = sibling.strip()
                    if text.lower().startswith("on "):
                        trakt_network = text[3:].strip()
                        break

    # # Country of origin
    trakt_country_of_origin = "N.A."
    label = soup.find("label", string="Country")
    trakt_country_of_origin = str(label.next_sibling).strip()

    # # Genres
    trakt_genres = "N.A."
    label = soup.find("label", string="Genres")
    if label:
        trakt_genres_temp = []
        for sibling in label.next_siblings:
            if (
                getattr(sibling, "name", None) == "span"
                and sibling.get("itemprop") == "genre"
            ):
                trakt_genres_temp.append(sibling.text.strip())
        if len(trakt_genres_temp) > 0:
            trakt_genres = trakt_genres_temp

    # # Wikipedia link
    link = soup.find("a", id="external-link-wikipedia")
    trakt_wiki_link = link["href"] if link else None

    trakt_data = {
        "trakt_title": trakt_title,
        "trakt_rating_imdb": trakt_rating_imdb,
        "trakt_vote_count_imdb": trakt_vote_count_imdb,
        "trakt_full_runtime": trakt_full_runtime,
        "trakt_avg_ep_runtime": trakt_avg_ep_runtime,
        "trakt_network": trakt_network,
        "trakt_country_of_origin": trakt_country_of_origin,
        "trakt_genres": trakt_genres,
        "trakt_wiki_link": trakt_wiki_link,
    }

    return trakt_data


def scrape_trakt_from_top_tv_data(imdb_data):
    data = []

    i = 0
    for imdb_series_data in imdb_data:
        i += 1
        trakt_data = scrape_trakt_page(imdb_series_data)
        imdb_series_data.update(trakt_data)
        data.append(imdb_series_data)

        if i == 3:
            break

    return data
