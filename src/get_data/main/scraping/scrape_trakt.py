import re
import requests

from bs4 import BeautifulSoup

from main.vars import BROWSER_LIKE_HEADERS

from main.scraping.scraping_shared import for_loop_scrape_logic


def parse_and_format_number(s, trakt_title):
    s = s.strip().lower()
    multiplier = 1

    if s.endswith("k"):
        multiplier = 1_000
        s = s[:-1]
    elif s.endswith("m"):
        multiplier = 1_000_000
        s = s[:-1]

    try:
        number = float(s)
    except ValueError:
        raise ValueError(f"Invalid number format: {s}")

    value = int(number * multiplier)
    return f"{value:,}"


def slugify(text):
    # Lowercase, replace spaces with dashes, remove non-alphanumeric except dash
    text = text.lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text


def scrape_trakt_page(series_data, iteration):
    # ## BACKUP IF NO TRAKT PAGE IS FOUND OR MISSING DATA
    trakt_data = {
        "trakt_title": "N.A.",
        "trakt_rating_imdb": "N.A.",
        "trakt_vote_count_imdb": "N.A.",
        "trakt_full_runtime_min": "N.A.",
        "trakt_avg_ep_runtime_min": "N.A.",
        "trakt_networks": "N.A.",
        "trakt_country_of_origin": "N.A.",
        "trakt_genres": "N.A.",
        "trakt_studios": "N.A.",
        "trakt_creators": "N.A.",
        "trakt_num_of_episodes": "N.A.",
        "trakt_num_of_seasons": "N.A.",
        "trakt_series_regulars": "N.A.",
        "trakt_guest_stars": "N.A.",
        "trakt_wiki_link": "N.A.",
    }

    # ## CHECK IF THE PAGE CAN BE SCRAPED
    required_keys = ["imdb_id", "imdb_ongoing", "imdb_title", "imdb_year_start"]
    try:
        imdb_id = series_data["imdb_id"]
        imdb_ongoing = series_data["imdb_ongoing"]
        imdb_title = series_data["imdb_title"]
        imdb_year_start = series_data["imdb_year_start"]
    except KeyError:
        missing_keys = [key for key in required_keys if key not in series_data]
        print(
            f"\nError: Missing required key(s): {', '.join(f"'{key}'" for key in missing_keys)}\n"
            "These are needed when scraping Trakt.\n"
            "This likely means the IMDB Top TV data has not been scraped yet.\n"
            "Make sure to run the IMDB Top TV scraping before attempting Trakt scraping.\n"
        )
        raise

    url = f"https://trakt.tv/search/imdb/{imdb_id}"
    res = requests.get(url, headers=BROWSER_LIKE_HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    # ## CHECK IF THERE IS A MOVIE AND A SERIES OR MULTIPLE SERIES WITH THE SAME IMDB ID
    # If you get correctly redirected to the show page, the final URL contains /shows/
    if "/shows/" not in res.url:
        soup = BeautifulSoup(res.text, "html.parser")

        results = soup.find_all("div", attrs={"data-type": "show"})

        possible_show_links = []
        for show_div in results:
            possible_show_links.append(show_div.get("data-url", "").strip(" /"))

        if len(possible_show_links) == 0:
            # there is no trakt page for the searched show from imdb
            return trakt_data
        elif len(possible_show_links) == 1:
            show_part_link = possible_show_links[0]
        else:
            show_part_link = None
            slug_imdb_title = slugify(imdb_title)

            for possible_show_link in possible_show_links:
                if possible_show_link.endswith(f"-{imdb_year_start}"):
                    show_part_link = possible_show_link
                    break  # priority match - exit immediately
                else:
                    slug_possible_show_link = slugify(
                        possible_show_link.removeprefix("shows/")
                    )
                    if slug_imdb_title == slug_possible_show_link:
                        show_part_link = possible_show_link  # possible match - save it, but keep looping
            if not show_part_link:
                # could find the correct trakt page from imdb_id
                return trakt_data

        actual_show_url = f"https://trakt.tv/{show_part_link}"

        # Redo the request and define new soup now actaully the show's page
        res = requests.get(actual_show_url, headers=BROWSER_LIKE_HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

    # ## Title
    trakt_title = soup.select_one("div.mobile-title h1").next_element.strip()

    # ## IMDB rating and Vote count
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
                trakt_vote_count_imdb = parse_and_format_number(
                    span.get_text(strip=True), trakt_title
                )

    # ## Avg runtime
    trakt_avg_ep_runtime_min = "N.A."
    label = soup.find("label", string="Runtime")
    if label:
        span = label.find_next_sibling("span", class_="humanized-minutes")
        if span:
            trakt_avg_ep_runtime_min = span.get("data-full-minutes").strip(" m")

    # ## Total runtime
    trakt_full_runtime_min = "N.A."
    label = soup.find("label", string="Total Runtime")
    if label:
        span = label.find_next_sibling("span", class_="humanized-minutes")
        if span:
            trakt_full_runtime_min = span.get("data-full-minutes").strip(" m")

        # ## Number of episodes
        trakt_num_of_episodes = "N.A."
        span = label.find_next_sibling("span", class_="alt")
        match_episodes_count = re.search(r"\((\d+)\s+episodes?\)", span.text)
        if match_episodes_count:
            trakt_num_of_episodes = match_episodes_count.group(1)

    # ## Network
    trakt_networks = "N.A."
    if imdb_ongoing == "No":
        label = soup.find("label", string="Network")
        if not label:
            label = soup.find("label", string="Networks")
        if label:
            full_text = ""
            for sibling in label.next_siblings:
                if isinstance(sibling, str):
                    full_text += sibling.strip() + " "
                # elif sibling.name == "span" and "studios-more" in sibling.get("class", []):
                #     full_text += sibling.get_text(strip=True) + " "
            network_list = [s.strip() for s in full_text.split(",") if s.strip()]
            if network_list:
                trakt_networks = network_list

    if trakt_networks == "N.A.":
        label = soup.find("label", string="Airs")
        if label:
            siblings = list(label.next_siblings)
            for sibling in reversed(siblings):
                if isinstance(sibling, str):
                    text = sibling.strip()
                    if text.lower().startswith("on "):
                        trakt_networks = [text[3:].strip()]
                        break

    # ## Country of origin
    trakt_country_of_origin = "N.A."
    label = soup.find("label", string="Country")
    trakt_country_of_origin = str(label.next_sibling).strip()

    # ## Genres
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

    # ## Studios
    trakt_studios = "N.A."
    label = soup.find("label", string="Studios")
    if not label:
        label = soup.find("label", string="Studio")
    if label:
        full_text = ""
        for sibling in label.next_siblings:
            if isinstance(sibling, str):
                full_text += sibling.strip() + " "
            elif sibling.name == "span" and "studios-more" in sibling.get("class", []):
                full_text += sibling.get_text(strip=True) + " "
        studios_list = [s.strip() for s in full_text.split(",") if s.strip()]
        if studios_list:
            trakt_studios = studios_list

    # ## Creators
    trakt_creators = "N.A."
    label = soup.find("label", string="Creators")
    if not label:
        label = soup.find("label", string="Creator")
    if label:
        creators_list = []
        for sibling in label.next_siblings:
            if sibling.name == "a" and "creators-expand" not in sibling.get(
                "class", []
            ):
                creators_list = sibling.get_text(strip=True)
        if creators_list:
            trakt_creators = creators_list

    # ## Extract series regulars
    trakt_series_regulars = []
    for actor in soup.select("#series-regulars-actors li[itemprop='actor']"):
        name = actor.select_one(".name").text.strip().replace("\u0131", "i")
        trakt_series_regulars.append(name)

    # ## Number of seasons
    trakt_num_of_seasons = "N.A."
    label = soup.find("a", class_="season-count")
    match_seasons_count = re.search(r"(\d+)\s+Seasons?", label.get_text(strip=True))
    if match_seasons_count:
        trakt_num_of_seasons = match_seasons_count.group(1)

    # ## Extract (max) guest stars
    max_guest_stars = 15
    trakt_guest_stars = []
    for actor in soup.select("#guest-stars-actors li[itemprop='actor']"):
        name = actor.select_one(".name").text.strip().replace("\u0131", "i")
        trakt_guest_stars.append(name)
        # Stop after collecting max_guest_stars names
        if len(trakt_guest_stars) >= max_guest_stars:
            break

    # ## Wikipedia link
    link = soup.find("a", id="external-link-wikipedia")
    trakt_wiki_link = link["href"].strip(" /") if link else None

    # Take snapshot of locals once
    local_vars = locals()

    # Update trakt_data keys if matching local variables exist (and not None and not "N.A.")
    for key in trakt_data:
        if key in local_vars:
            val = local_vars[key]
            if val is not None and val != "N.A.":
                trakt_data[key] = local_vars[key]

    return trakt_data


def scrape_trakt_from_data_imdb(data):
    id_whitelist = []
    # id_whitelist = ["tt1533395"] # Life 2009 series also has a movie with same imdb id
    # id_whitelist = ["tt1628033"] # Top Gear 2002 series also has a korean version with same imdb id
    # id_whitelist = ["tt0795176"] # Planet Earth 2006
    return for_loop_scrape_logic(
        "trakt", scrape_trakt_page, data, id_whitelist=id_whitelist
    )
