#!/usr/bin/env python
import pandas as pd
import yaml
from openpyxl import load_workbook


def clean(resource_configs):
    filepath = resource_configs["raw"]["path"]
    metadata = yaml.safe_load(open(filepath + ".meta.yaml", "r"))

    if resource_configs["raw"]["format"] == "csv":
        print(f"Reading CSV from {filepath:s}.")
        df = pd.read_csv(filepath,
                         encoding=resource_configs["raw"]["encoding"],
                         sep=resource_configs["raw"]["sep"],
                         na_values=resource_configs["raw"]["na_values"],
                         quotechar=resource_configs["raw"]["quotechar"])
    elif resource_configs["raw"]["format"] == "xlsx":
        print(f"Reading XLSX from {filepath:s}.")
        wb = load_workbook(resource_configs["raw"]["path"])
        ws = wb[resource_configs["raw"]["sheet"]]
        df = pd.DataFrame(ws.values)
        if resource_configs["raw"]["header"]:
            df, df.columns = df[1:], df.iloc[0]  # 1st row to headers
    else:
        raise NotImplementedError

    # Rename columns
    if "rename" in resource_configs["raw"].keys(): 
        df = df.rename(resource_configs["raw"]["rename"], axis=1)

    # Save
    filepath = resource_configs["processed"]["path"]
    print(f"Saving processed data to {filepath:s}.")
    df.to_csv(filepath, index=False)
    yaml.safe_dump(metadata,
                   open(filepath + ".meta.yaml", "w"),
                   default_flow_style=False,
                   allow_unicode=True)


def main():
    configs = yaml.safe_load(open("configs.yaml", "r"))

    for resource in configs["data"].keys():
        print(f"Cleaning {resource:s}.")
        clean(resource_configs=configs["data"][resource], )


if __name__ == "__main__":
    main()