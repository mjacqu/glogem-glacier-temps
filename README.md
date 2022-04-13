# GloGlaT

## Project description
As part of a project aimed at estimating the temperature regime for all RGI glaciers, we are compiling an open-access database of englacial temperature measurements. So far, we have digitized records from published papers from 72 different glaciers and ice caps, but wanted to reach out to the scientific community to solicit additional datasets.

## Data structure
- [`studies.csv`](01_studies.csv): Table of all studies that have been included to date. The column "catalogued" indicates whether data from the study has been incorporated into the database.

- [`measurement_info.csv`](02_measurement_info.csv):
Metadata about each individual temperature profile.

- [`temperatures.csv`](03_temperatures.csv):
Depth vs. temperature data linked to the the data in `measurement_info.csv` and `studies.csv` via `study_id` and `measurement_id`

## How to contribute
If you would like to contribute data, please send an email to jacquemart@vaw.baug.ethz.ch

Shared datasets should ideally include:

Depth vs. temperature data
Measurement date
Measurement location (ideally Lat/Long and elevation)
Whether the borehole reached the bottom
Any additional descriptions of the site, notes etc.
Author / team

We also welcome submissions of datasets that have already been digitized, because it allows us to assess the accuracy of the digitization process.
