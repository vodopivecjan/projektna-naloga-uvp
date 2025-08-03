from pprint import pprint


from ddgs import DDGS

from wikipedia import wikipedia as wiki

from wikipedia.exceptions import DisambiguationError, PageError


def rank_results(row, results):
    show_name_lower = row["title"].lower()
    year_start = row["year_start"]

    penalty_words = {
        "season",
        "episode",
        "episodes",
        "list of",
        "series overview",
        "film",
        "franchise",
        "category",
    }
    boost_words = {"series", "tv"}
    wikipedia_suffixes = [
        " - simple english wikipedia, the free ...",
        # " - wikipedia, the free encyclopedia"
    ]

    def clean_title(title):
        title = title.lower()
        for suffix in wikipedia_suffixes:
            if title.endswith(suffix):
                return title.removesuffix(suffix).strip()
        return title

    def score(result):
        title = clean_title(result["title"])

        # Lower weight on similarity
        # ratio = difflib.SequenceMatcher(None, show_name_lower, title).ratio() * 0.6

        # Heavier penalty for word count mismatch
        word_penalty = abs(len(title.split()) - len(show_name_lower.split())) * 0.2

        # Penalty if unwanted words in title
        has_penalty = any(w in title for w in penalty_words)
        penalty = word_penalty + (0.5 if has_penalty else 0)

        # Boosts for keywords
        boost = 0
        if any(w in title for w in boost_words):
            boost += 0.4

        # Boost for year
        if year_start in title:
            boost += 1

        if year_start in result["body"]:
            boost += 1

        # return ratio - penalty + boost

    return sorted(results, key=score, reverse=True)


def find_wikipedia_page(row):
    show_name = row["title"]
    year_start = row["year_start"]
    # show_imdb_link= row["link"]

    try:
        # intitle:{show_name} site:wikipedia.com -episodes -season TV Series
        search_query = f'en.wikipedia.org "{show_name}" TV Series {year_start}'

        # Perform the search using DDGS().text() and limit to one result.
        # Ensure 'region' is set for more relevant results if needed, e.g., 'wt-en-si' for English in Slovenia.
        results = DDGS().text(search_query, backend="google", max_results=13)

        filtered_results = []
        for result in results:
            url = result.get("href")

            if "simple.wikipedia.org" in url:
                url = url.replace("simple.wikipedia.org", "en.wikipedia.org")

            if "en.wikipedia.org" in result:
                filtered_results.append(result)

        results = rank_results(row, results)

        pprint(results)

        if results:
            for result in results:
                # Add an extra check to ensure the URL actually belongs to Wikipedia
                if url and "en.wikipedia.org" in url:
                    if all(
                        substr not in url.lower() for substr in ("list_of", "episodes")
                    ):
                        return url
        else:
            return None  # No results found for the query
    except Exception as e:
        print(f"An error occurred during DuckDuckGo search: {e}")
        return None


def find_scrape_wikipedia(row):
    show_name = row["title"]
    year_start = row["year_start"]
    rank = row["rank"]

    # if show_name != "Band of Brothers":
    #     return
    # time.sleep(3)
    print()
    print()
    url = find_wikipedia_page(row)
    print(rank, show_name, year_start)
    print(url)

    # print(url)

    # show_name = row["title"]
    # show_imdb_link= row["link"]

    # print()
    # print(show_name, show_imdb_link)
    # titles = wiki.search(show_name)

    # pprint(titles)

    # sorted_titles = sorted(titles, key=lambda s: "series" not in s.lower())

    # pprint(sorted_titles)

    # page_found = False
    # for title in sorted_titles:
    #     try:
    #         page = wiki.page(title, auto_suggest=False)
    #         html = page.html()  # get raw HTML from wikipedia module

    #         print(html)
    #         # soup = BeautifulSoup(html, "html.parser")

    #         # # Look for IMDb links anywhere on the page
    #         # for a in soup.find_all("a", href=True):
    #         #     if show_imdb_link in a["href"]:
    #         #         print(True)
    #         #         page_found = True
    #         #         break

    #         # if page_found:
    #         #     break
    #     except PageError:
    #         continue
    #     except DisambiguationError as e:
    #         # Handle disambiguation pages, try to find a more specific link
    #         print(f"Disambiguation page for {title}")
    #         for option in e.options:
    #             if title.lower() in option.lower() and ("tv series" in option.lower() or "television series" in option.lower()):
    #                 try:
    #                     page = wiki.page(option, auto_suggest=False)
    #                     return page.url
    #                 except (PageError, DisambiguationError):
    #                     continue
