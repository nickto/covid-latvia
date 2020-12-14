import pandas as pd
import requests
import yaml


def download_resource(resource_configs, host):
    # Get resource properties
    endpoint = "api/3/action/package_show"
    url = f"{host:s}/{endpoint:s}"
    print(f"Downloading resource properties from {url:s}.")
    response = requests.get(url, params={"id": resource_configs["id"]})
    assert response.ok
    dataset_metadata = response.json()
    assert dataset_metadata["success"]

    resources = response.json()["result"]["resources"]
    resource_meta = [
        r for r in resources if r["name"] == resource_configs["name"]
    ][0]

    # Download metadata
    data_url = resource_meta["url"]
    print(f"Downloading from {url:s}.")
    response = requests.get(data_url)
    assert response.ok
    data = response.content

    # Write data
    filepath = resource_configs["raw"]["path"]
    print(f"Writing data to {filepath:s}.")
    with open(filepath, "wb") as f:
        f.write(data)

    # Write metadata
    filepath += ".meta.yaml"
    print(f"Writing metadata to {filepath + '.meta.yaml':s}.")
    yaml.safe_dump(resource_meta,
                   open(filepath, "w"),
                   default_flow_style=False,
                   allow_unicode=True)


def main():
    configs = yaml.safe_load(open("configs.yaml", "r"))

    for resource in configs["data"].keys():
        print(f"Downloading {resource:s} data.")
        download_resource(
            resource_configs=configs["data"][resource],
            host=configs["open_data_portal"]["host"],
        )


if __name__ == "__main__":
    main()