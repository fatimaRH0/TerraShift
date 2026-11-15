"""
TerraShift - Download the NASA satellite data listed in the functional document
--------------------------------------------------------------------------------
Sources:
  - SMAP L4        soil moisture             (AppEEARS)
  - MODIS MOD13Q1  NDVI / EVI                (AppEEARS)
  - ECOSTRESS LSTE surface temperature       (AppEEARS)
  - Landsat C2 L2  reflectance -> NDVI, surface temperature (USGS Collection 2,
                   via Microsoft Planetary Computer)
  - SRTM           elevation                 (AppEEARS)
  - GPM IMERG      precipitation             (GES DISC data rods)
  (NASA POWER weather is downloaded by app.py itself)

Before the first run:
  1. Create a FREE NASA Earthdata account: https://urs.earthdata.nasa.gov/users/new
  2. Log in once on https://appeears.earthdatacloud.nasa.gov  (accept the terms)

Run:
    python download_satellite.py
The field location comes from src/config.py (FIELD_NAME, LATITUDE, LONGITUDE), or:
    python download_satellite.py --lat 31.44 --lon -9.73 --name my_place
(the dashboard starts it like this with its "Download satellite data" button).
AppEEARS can take from a few minutes to ~1 hour. If you stop the script,
run it again: it resumes the same request instead of starting a new one.
"""

import json
import os
import sys
from datetime import date, timedelta

import requests

from src import config
from src.earthdata import get_credentials, EarthdataSession
from src.satellite import clean_source, save_source, file_path, save_place
from src.sources import appeears
from src.sources.gpm import fetch_gpm_daily, GpmError
from src.sources.landsat import fetch_landsat_point
from src.sources.pc_nasa import fetch_modis_point, fetch_nasadem_point


# Place to download. Defaults come from src/config.py; the app passes --lat --lon --name.
NAME, LAT, LON = config.FIELD_NAME, config.LATITUDE, config.LONGITUDE


def date_range():
    end = date.today() - timedelta(days=config.NASA_DELAY_DAYS)
    start = end - timedelta(days=config.NUM_DAYS)
    return start, end


# ---------------------------------------------------------
# AppEEARS part
# ---------------------------------------------------------
def build_layer_list():
    """Find the newest version of each product and the real layer names."""
    print("🔎 Looking up products in AppEEARS ...")
    products = appeears.list_products()
    layers, plan = [], {}
    for source, info in config.APPEEARS_PRODUCTS.items():
        try:
            product = appeears.choose_version(products, info["product"], info.get("version"))
            names = appeears.pick_layers(appeears.list_layers(product), info["layers"])
        except appeears.AppeearsError as error:
            print(f"   ⚠️  {source}: {error}")
            continue
        print(f"   ✔ {source:10s} {product:18s} {names}")
        plan[source] = {"product": product, "layers": names}
        layers += [{"product": product, "layer": name} for name in names]
    return layers, plan


def run_appeears(user, password, start, end):
    token = appeears.login(user, password)
    print("✅ Logged in to AppEEARS")

    task_file = os.path.join(config.DATA_DIR, f"{NAME}_appeears_task.json")
    request_id = f"{LAT},{LON},{start},{end}"

    # Resume a previous request if it is for the same field and dates
    saved = {}
    if os.path.exists(task_file):
        with open(task_file) as f:
            saved = json.load(f)
    if saved.get("request_id") == request_id:
        task_id, plan = saved["task_id"], saved["plan"]
        print(f"↩️  Resuming AppEEARS request {task_id}")
    else:
        layers, plan = build_layer_list()
        if not layers:
            print("❌ No AppEEARS layers found.")
            return
        task_id = appeears.submit_task(token, f"fieldshift-{NAME}",
                                       LAT, LON, start, end, layers)
        with open(task_file, "w") as f:
            json.dump({"request_id": request_id, "task_id": task_id, "plan": plan}, f, indent=2)
        print(f"📨 Request submitted: {task_id}")

    appeears.wait_for_task(token, task_id)

    out_dir = os.path.join(config.DATA_DIR, "appeears", NAME)
    paths = appeears.download_results(token, task_id, out_dir)
    clean_appeears_files(paths, plan)


def clean_appeears_files(paths, plan):
    print("🧹 Cleaning the data ...")
    for source, info in plan.items():
        if source not in config.APPEEARS_PRODUCTS:     # e.g. an old request that still had HLS
            print(f"   ⏭️  {source}: not used any more, skipped")
            continue
        # result files are named like "...-MOD13Q1-061-results.csv"
        short = info["product"].split(".")[0].replace("_", "-")
        matches = [p for p in paths if short.lower() in os.path.basename(p).lower().replace("_", "-")]
        if not matches:
            print(f"   ⚠️  {source}: no result file found")
            continue
        raw = appeears.read_results(matches[0], info["layers"], keep_time=(source == "ecostress"))
        save_source(NAME, source, clean_source(source, raw))


# ---------------------------------------------------------
# GPM part
# ---------------------------------------------------------
def run_gpm(user, password, start, end):
    print("🌧️  Downloading GPM IMERG precipitation ...")
    session = EarthdataSession(user, password)
    try:
        # IMERG Final is ~4 months late: stop the request before that
        df = fetch_gpm_daily(user, password, session, LAT, LON,
                             start, end - timedelta(days=120))
    except GpmError as error:
        print(f"   ⚠️  GPM not downloaded: {error}")
        return
    save_source(NAME, "gpm", df)


# ---------------------------------------------------------
# Landsat part
# ---------------------------------------------------------
def run_landsat(start, end):
    print("🛰️  Reading Landsat Collection 2 Level-2 scenes ...")
    df = fetch_landsat_point(LAT, LON, start, end, config.LANDSAT_MAX_CLOUD)
    if df.empty:
        print("   ⚠️  No clear Landsat scene found for this period.")
        return
    save_source(NAME, "landsat", df)


# ---------------------------------------------------------
# No-account part: MODIS + NASADEM from the Planetary Computer copy of NASA LP DAAC
# ---------------------------------------------------------
def run_free_nasa(start, end):
    print("⛰️  Reading NASADEM elevation (NASA SRTM, no account needed) ...")
    try:
        save_source(NAME, "srtm", fetch_nasadem_point(LAT, LON))
    except Exception as error:
        print(f"   ⚠️  NASADEM error: {error}")
    print("🌿 Reading MODIS NDVI (NASA, no account needed) ...")
    try:
        save_source(NAME, "modis", fetch_modis_point(LAT, LON, start, end))
    except Exception as error:
        print(f"   ⚠️  MODIS error: {error}")


def main():
    """
    python download_satellite.py              -> everything
    python download_satellite.py gpm          -> only GPM
    python download_satellite.py landsat      -> only Landsat
    python download_satellite.py appeears     -> only SMAP / MODIS / ECOSTRESS / SRTM
    python download_satellite.py reprocess    -> clean the downloaded AppEEARS files again
    """
    global NAME, LAT, LON
    args = sys.argv[1:]
    for flag in ("--lat", "--lon", "--name"):
        if flag in args:
            i = args.index(flag)
            value = args[i + 1]
            if flag == "--lat":
                LAT = float(value)
            elif flag == "--lon":
                LON = float(value)
            else:
                NAME = value
            del args[i:i + 2]
    wanted = set(a.lower() for a in args) or {"gpm", "landsat", "free", "appeears"}

    if wanted == {"reprocess"}:
        # Clean the already-downloaded AppEEARS files again (no internet needed)
        import glob
        task_file = os.path.join(config.DATA_DIR, f"{NAME}_appeears_task.json")
        with open(task_file) as f:
            plan = json.load(f)["plan"]
        paths = glob.glob(os.path.join(config.DATA_DIR, "appeears", NAME, "*results.csv"))
        clean_appeears_files(paths, plan)
        return
    os.makedirs(config.DATA_DIR, exist_ok=True)
    save_place(NAME, LAT, LON)
    start, end = date_range()
    print(f"📍 {NAME} ({LAT}, {LON})  {start} → {end}\n")

    # NASADEM, MODIS and Landsat need no account: always downloaded first
    if "free" in wanted:
        run_free_nasa(start, end)
        print()
    if "landsat" in wanted:
        try:
            if os.path.exists(file_path(NAME, "landsat")) and len(wanted) > 1:
                print("🛰️  Landsat already downloaded (delete data/*_landsat.csv to download again)")
            else:
                run_landsat(start, end)
        except Exception as error:
            print(f"   ⚠️  Landsat error: {error}")
        print()

    # SMAP, ECOSTRESS and GPM need a free NASA Earthdata account (saved once in a .env file)
    user, password = get_credentials(ask=not os.environ.get("TERRASHIFT_NO_PROMPT"))
    if not (user and password):
        print("ℹ️  No Earthdata account found: SMAP, ECOSTRESS and GPM skipped "
              "(soil moisture and rain still come from NASA POWER).")
        print("\n🎉 Done!")
        return
    if "gpm" in wanted:
        try:
            if os.path.exists(file_path(NAME, "gpm")) and len(wanted) > 1:
                print("🌧️  GPM already downloaded (delete data/*_gpm.csv to download again)")
            else:
                run_gpm(user, password, start, end)
        except Exception as error:          # keep going even if GPM fails
            print(f"   ⚠️  GPM error: {error}")
        print()

    if "appeears" in wanted:
        try:
            run_appeears(user, password, start, end)
        except appeears.AppeearsError as error:
            print(f"❌ AppEEARS: {error}")
            return
        except requests.exceptions.ConnectionError:
            print("❌ Internet connection lost. Run the script again: it resumes the same request.")
            return

    print("\n🎉 Done! Start the dashboard with:  streamlit run app.py")


if __name__ == "__main__":
    main()
