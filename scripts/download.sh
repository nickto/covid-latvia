#!/usr/bin/env bash
# COVID cases
url=https://data.gov.lv/dati/dataset/f01ada0a-2e77-4a82-8ba2-09cf0cf90db3/resource/d499d2f0-b1ea-4ba2-9600-2c701b03bd4a/download/covid_19_izmeklejumi_rezultati.csv
curl $url > data/covid_19_izmeklejumi_rezultati.csv

url=https://data.gov.lv/dati/dataset/f01ada0a-2e77-4a82-8ba2-09cf0cf90db3/resource/dc3bac3e-0330-427e-bfe0-8d5cb0cf9383/download/covid_19_izmeklejumi_rezultati_metadata.json
curl $url > data/covid_19_izmeklejumi_rezultati_metadata.json

# COVIDA cases by region
url=https://data.gov.lv/dati/dataset/e150cc9a-27c1-4920-a6c2-d20d10469873/resource/492931dd-0012-46d7-b415-76fe0ec7c216/download/covid_19_pa_adm_terit.csv
curl $url > data/covid_19_pa_adm_terit.csv

url=https://data.gov.lv/dati/dataset/e150cc9a-27c1-4920-a6c2-d20d10469873/resource/dd21217a-baa9-4092-a459-fd37e00f80fd/download/covid_19_pa_adm_terit_metadata.json
curl $url > data/covid_19_pa_adm_terit_metadata.json