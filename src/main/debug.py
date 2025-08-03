import time
from pprint import pprint

def execute_and_time(func, *args, **kwargs):
    start = time.time()
    print(f"Started execution ({func.__name__}): {time.strftime("%H:%M:%S %d/%m/%Y", time.localtime(start))}")
    return_value = func(*args, **kwargs)
    end = time.time()
    elapsed = end - start
    print(f"Elapsed time ({func.__name__}): {elapsed:.2f} seconds")

    return return_value

def pp(msg):
    pprint(msg)