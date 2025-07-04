def scrape_imdb_top_tv():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)  # Set to False if you want to see it
        page = browser.new_page()
        url = "https://www.imdb.com/chart/toptv/"
        page.goto(url)

        page.wait_for_selector("ul.ipc-metadata-list")

        items = page.query_selector_all("ul.ipc-metadata-list > li")

        shows = []
        for i, item in enumerate(items, 1):
            # title_el = item.query_selector("h3.ipc-title__text")
            # rating_el = item.query_selector("span.ipc-rating-star--rating")
            # votes_el = item.query_selector("span.ipc-rating-star--voteCount")

            # title = title_el.inner_text().split(". ", 1)[-1] if title_el else None
            # rating = rating_el.inner_text() if rating_el else None
            # votes = votes_el.inner_text().strip(" ()\xa0") if votes_el else None

            # print(f"{i}. {title} - Rating: {rating}, Votes: {votes}")

            entry = {}

            title = item.query_selector("h3.ipc-title__text").inner_text()
            # split the rank from title
            title = title.removeprefix(f"{i}. ") if title else None
            entry["title"] = title

            entry["rank"] = i

            # url
            link_tag = item.query_selector("a.ipc-title-link-wrapper")
            link = (
                link_tag.get_attribute("href")
                if link_tag.get_attribute("href")
                else None
            )
            parsed = urlparse(link)
            entry["link"] = parsed.path

            # metadata spans
            metadata_spans = item.query_selector_all(".cli-title-metadata span")

            ## years
            years_text = (
                metadata_spans[0].inner_text() if len(metadata_spans) > 0 else None
            )
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
            num_of_episodes = (
                metadata_spans[1].inner_text() if len(metadata_spans) > 1 else None
            )
            entry["num_of_episodes"] = num_of_episodes.removesuffix(" eps")

            ## parental ranting
            entry["parental_rating"] = (
                metadata_spans[2].inner_text() if len(metadata_spans) > 2 else None
            )

            ## series type
            entry["series_type"] = (
                metadata_spans[3].inner_text() if len(metadata_spans) > 3 else None
            )

            # user rating
            user_rating_tag = item.query_selector("span.ipc-rating-star--rating")
            entry["user_rating"] = (
                user_rating_tag.inner_text().strip() if user_rating_tag else None
            )

            # count of user ratings
            votes_tag = item.query_selector("span.ipc-rating-star--voteCount")
            user_votes_count = votes_tag.inner_text() if votes_tag else None
            start = user_votes_count.find("(")
            end = user_votes_count.find(")", start)
            if start != -1 and end != -1:
                entry["user_votes_count"] = user_votes_count[start + 1 : end]
            else:
                entry["user_votes_count"] = None

            shows.append(entry)

        browser.close()

    return shows
