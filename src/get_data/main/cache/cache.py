import pickle
from pathlib import Path

from main.vars import TEMP_FOLDER_PATH


def save_cache(cache_name, data):
    cache_file = Path(TEMP_FOLDER_PATH) / f"{cache_name}.pkl"
    with open(cache_file, "wb") as f:
        pickle.dump(data, f)


def load_cache(cache_name):
    cache_file = Path(TEMP_FOLDER_PATH) / f"{cache_name}.pkl"
    if cache_file.exists():
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    else:
        raise FileNotFoundError(
            f"Error: The cache file at '{cache_file.resolve()}' was not found.\n"
            "Maybe it has been saved wrong."
        )

def delete_cache_from_list_no_error(caches_list):
    for cache_name in caches_list:
        cache_file = Path(TEMP_FOLDER_PATH) / f"{cache_name}.pkl"
        cache_file.unlink(missing_ok=True)
        
