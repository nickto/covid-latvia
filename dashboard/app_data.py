import pandas as pd
import functools
import yaml

@functools.lru_cache()
def get_configs():
    return yaml.safe_load(open("configs.yaml", "r"))

def read_cases():
    configs = get_configs()
    df = pd.read_csv(configs["data"]["cases"]["processed"]["path"])
    df = df.sort_values("date")
    return df

def read_cases_meta():
    configs = get_configs()
    filepath = configs["data"]["cases"]["clean"]["path"] + ".meta.yaml"
    return yaml.safe_load(open(filepath, "r"))