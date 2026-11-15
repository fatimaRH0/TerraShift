# TerraShift — the right crop, every season, from NASA data

A decision-support app for farmers. Pick a field, and TerraShift reads the NASA data for
that place, sums it up in one sentence, estimates the drought risk for the next 14 days,
and suggests the crop to grow this season from the last three seasons and the water available.
Available in English, French and Arabic.

## Install (once)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```
venv\Scripts\activate
streamlit run app.py
```
Use the **Demo field (Meknès)** button to open a field whose NASA data is already included.

## Data
Downloaded automatically, in the background, when a place is chosen:
- **No account needed:** NASA POWER (weather), MODIS (NDVI), Landsat 8-9 (NDVI, surface
  temperature, with USGS), NASADEM / SRTM (elevation).
- **Free NASA Earthdata account (optional):** SMAP, ECOSTRESS, GPM IMERG. Enter the account
  once in the sidebar, or put it in the app's Secrets when hosting
  (see `.streamlit/secrets.toml.example`). Log in once on
  https://appeears.earthdatacloud.nasa.gov and approve "NASA GESDISC DATA ARCHIVE" in your
  Earthdata profile.

The full list of sources is in the app, under "References and data sources".

## What is in the app
Overview (verdict, indicators, alerts) · Map · History · 3D farm · Crops (suggestion and
FAO-56 water needs) · Drought risk (Random Forest) · Assistant · Glossary · one-page report.

## Limits
NASA POWER is regional (about 50 km). The verdict, the crop suggestion and the drought risk
are computed by TerraShift: they support decisions and are not official NASA forecasts.
