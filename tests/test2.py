import re

span = "(62 episodes)"
match_episodes_count = re.search(r"\((\d+)\s+episodes?\)", span)
if match_episodes_count:
    print(match_episodes_count)
    print(match_episodes_count.group(1))