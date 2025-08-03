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
