def for_loop_scrape_logic(
    source,
    scraper_func,
    data_items=None,
    id_whitelist=None,
    id_blacklist=None,
):
    # ## Check for possible errors
    possible_sources = {"trakt", "wiki"}
    if source not in possible_sources:
        raise ValueError(
            f"Invalid source '{source}'. Must be one of: {', '.join(f"'{item}'" for item in possible_sources)}"
        )

    map_source_label = {"trakt": "Trakt", "wiki": "Wikipedia"}

    source_label = map_source_label[source]

    # ## This program is created so that you can pass your
    # ## data object and just update specific entires or ignore specific entries
    # ## This behaviour is controlled by 'id_whitelist' nad 'id_blacklist'
    # ## if the blacklist contains some ids those will be skipped
    # ## if the whitelist contains some ids only those will be processed
    # ## usually only the whitelist is used, to just update a few entries
    # ## and not rerun everything just to update a specific entry

    print(f"\nStarted scraping {source_label}.")

    for i, series_data in enumerate(data_items):
        if i > 5:
            # ## DEMO
            # return data
            pass

        imdb_id = series_data["imdb_id"]
        imdb_title = series_data["imdb_title"]

        if id_blacklist and imdb_id in id_blacklist:
            continue

        if id_whitelist and imdb_id not in id_whitelist:
            continue

        try:
            print(
                f"Started scraping {source_label} for IMDB title: '{imdb_title}' ({imdb_id}) ({i + 1})."
            )
            scraped_data = scraper_func(series_data, i)
            series_data.update(scraped_data)
        except Exception:
            print(
                f"\nError: Something went wrong when scraping {source_label} page for title: '{imdb_title}' ({imdb_id}) ({i + 1}).\n"
            )
            raise

    print(f"Stopped scraping {source_label}.\n")

    return data_items
