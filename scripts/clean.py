#!/usr/bin/env python
import json
import pandas as pd
import yaml


def clean(input_data, input_metadata, output_data, output_metadata):
    metadata = json.load(open(input_metadata, "r"))
    df = pd.read_csv(input_data,
                     encoding=metadata["dialect"]["encoding"],
                     sep=metadata["dialect"]["delimiter"],
                     na_values=["...", chr(133)],
                     quotechar=metadata["dialect"]["quoteChar"])
    df.to_csv(output_data, index=False)

    yaml.safe_dump(metadata,
                   open(output_metadata, "w"),
                   default_flow_style=False,
                   allow_unicode=True)


def main():
    configs = yaml.safe_load(open("configs.yaml", "r"))
    
    for resource in ["cases", "cases_by_municipalities"]:
        clean(
            input_data=configs["data"][resource]["raw"]["data"],
            input_metadata=configs["data"][resource]["raw"]["metadata"],
            output_data=configs["data"][resource]["processed"]["data"],
            output_metadata=configs["data"][resource]["processed"]["metadata"],
        )


if __name__ == "__main__":
    main()