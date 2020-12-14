import pandas as pd
import requests
import yaml


def download_resource(id, host, output_data, output_metadata):
    # Get resource properties
    endpoint = "api/3/action/package_show"
    url = f"{host:s}/{endpoint:s}"
    response = requests.get(url, params={"id": id})
    assert response.ok
    dataset_metadata = response.json()
    assert dataset_metadata["success"]

    # Get URLs of resource data and metadata in a hacky way:
    # we know that data is CSV and metadata is JSON
    resources = response.json()["result"]["resources"]

    # Download metadata
    metadata_url = [i for i in resources if i["format"] == "JSON"][0]["url"]
    response = requests.get(metadata_url)
    assert response.ok
    metadata_raw = response.content
    with open(output_metadata, "wb") as f:
        f.write(metadata_raw)

    # Download data
    data_url = [i for i in resources if i["format"] == "CSV"][0]["url"]
    response = requests.get(data_url)
    assert response.ok
    data_raw = response.content
    with open(output_data, "wb") as f:
        f.write(data_raw)


def main():
    configs = yaml.safe_load(open("configs.yaml", "r"))

    for resource in ["cases", "cases_by_municipalities"]:
        download_resource(
            id=configs["data"][resource]["id"],
            host=configs["open_data_portal"]["host"],
            output_data=configs["data"][resource]["raw"]["data"],
            output_metadata=configs["data"][resource]["raw"]["metadata"],
        )


if __name__ == "__main__":
    main()