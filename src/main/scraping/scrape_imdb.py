from playwright.sync_api import sync_playwright


def scrape_entry_toptv(i, item):
    # ## Title
    imdb_title = (
        item.query_selector("h3.ipc-title__text").inner_text().split(". ", 1)[-1]
    )

    # ## Rank
    imdb_rank_toptv = i

    # ## IMDB id from link
    link_tag = item.query_selector("a.ipc-title-link-wrapper")
    imdb_id = link_tag.get_attribute("href").split("/?", 1)[0].removeprefix("/title/")

    metadata_spans = item.query_selector_all(
        ".cli-title-metadata span.cli-title-metadata-item"
    )

    # ## Years
    if len(metadata_spans) > 0:
        ## years
        years_text = metadata_spans[0].inner_text().replace("\u2013", "-")

        imdb_ongoing = "No"
        years_list = years_text.split("-", 1)
        if len(years_list) != 1:
            # show is finished or ongoing
            imdb_year_start = years_list[0].strip()
            year_end = years_list[1].strip()

            if not year_end:
                imdb_year_end = None
                imdb_ongoing = "Yes"
            else:
                imdb_year_end = year_end

        else:
            # the show ran for 1 year
            imdb_year_start = years_text
            imdb_year_end = years_text

    # ## Number of episodes
    # if len(metadata_spans) > 1:
    #     entry["num_of_episodes"] = (
    #         metadata_spans[1].inner_text().removesuffix(" eps")
    #     )

    # ## Parental ranting
    # if len(metadata_spans) > 2:
    #     entry["parental_rating"] = metadata_spans[2].inner_text()

    # ## Series type
    imdb_series_type = item.query_selector(
        ".cli-title-metadata span.cli-title-type-data"
    ).inner_text()

    # ## User rating
    # entry["user_rating"] = (
    #     item.query_selector("span.ipc-rating-star--rating").inner_text().strip()
    # )

    # ## Count of user ratings
    # votes_tag = item.query_selector("span.ipc-rating-star--voteCount")
    # entry["votes_count"] = (
    #     votes_tag.inner_text().strip(" ()\xa0") if votes_tag else None
    # )

    return {
        "imdb_title": imdb_title,
        "imdb_rank_toptv": imdb_rank_toptv,
        "imdb_id": imdb_id,
        "imdb_series_type": imdb_series_type,
        "imdb_ongoing": imdb_ongoing,
        "imdb_year_start": imdb_year_start,
        "imdb_year_end": imdb_year_end,
    }


def scrape_imdb_toptv():
    data_imdb_toptv = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)  # Set to False if you want to see it
        page = browser.new_page()
        url = "https://www.imdb.com/chart/toptv/"
        page.goto(url)

        # wait for all list items to load
        list_item_css_query = "ul.ipc-metadata-list > li"

        page.wait_for_selector(list_item_css_query)

        items = page.query_selector_all(list_item_css_query)

        for i, item in enumerate(items, 1):
            try:
                data = scrape_entry_toptv(i, item)
                data_imdb_toptv.append(data)
            except Exception:
                print(
                    f"\nError: Something went wrong when scraping IMDB top tv page for index {i}.\n"
                )
                raise

        browser.close()

    return data_imdb_toptv
