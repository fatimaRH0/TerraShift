"""
downloader.py - Start download_satellite.py for the current place from the dashboard,
in the background, and follow its progress (AppEEARS can take up to ~1 hour).
"""

import os
import subprocess
import sys

import streamlit as st

from src import config
from src.satellite import place_key

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@st.cache_resource
def _jobs():
    """Running downloads of this Streamlit server: {place key: Popen}."""
    return {}


def log_path(key):
    return os.path.join(ROOT, config.DATA_DIR, f"{key}_download.log")


def _job_key(lat, lon, tag):
    return place_key(lat, lon) + (f"_{tag}" if tag else "")


def start(lat, lon, user=None, password=None, parts=None, tag=""):
    """parts: which parts of download_satellite.py to run (default: all).
    tag: separates a second download of the same place (e.g. the Earthdata-account products)."""
    key = _job_key(lat, lon, tag)
    place = place_key(lat, lon)
    job = _jobs().get(key)
    if job is not None and job.poll() is None:
        return key                                     # already running
    os.makedirs(os.path.join(ROOT, config.DATA_DIR), exist_ok=True)
    from src.earthdata import get_credentials
    saved_user, saved_password = get_credentials(ask=False)     # .env, environment or app Secrets
    user, password = user or saved_user, password or saved_password
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", TERRASHIFT_NO_PROMPT="1",
               # never wait forever on one satellite image; retry a few times on network hiccups
               GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_CONNECTTIMEOUT="15", GDAL_HTTP_MAX_RETRY="4",
               GDAL_HTTP_RETRY_DELAY="3")
    if user and password:                              # typed in the app: passed to this run only
        env[config.EARTHDATA_USER_ENV] = user
        env[config.EARTHDATA_PASS_ENV] = password
    log = open(log_path(key), "w", encoding="utf-8")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    _jobs()[key] = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "download_satellite.py"),
         "--lat", f"{lat:.4f}", "--lon", f"{lon:.4f}", "--name", place] + list(parts or []),
        cwd=ROOT, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
        creationflags=flags)
    return key


def status(lat, lon, tag=""):
    """(state, last log lines). state: None (never started), 'running', 'done', 'failed'."""
    key = _job_key(lat, lon, tag)
    job = _jobs().get(key)
    lines = []
    if os.path.exists(log_path(key)):
        with open(log_path(key), encoding="utf-8", errors="replace") as f:
            lines = [ln.rstrip() for ln in f if ln.strip()]
    if job is None:
        return (None if not lines else "done"), lines
    code = job.poll()
    if code is None:
        import time
        if time.time() - os.path.getmtime(log_path(key)) > 300:      # no news for 5 minutes: stuck
            job.kill()
            return "failed", lines + ["⚠️ Stopped: no progress for 5 minutes (network). Try again."]
        return "running", lines
    return ("done" if code == 0 else "failed"), lines


def has_credentials():
    from src.earthdata import get_credentials
    user, password = get_credentials(ask=False)            # also reads the project's .env file
    return bool(user and password)


def account_name():
    from src.earthdata import get_credentials
    return get_credentials(ask=False)[0]


def save_credentials(user, password):
    """Saved once, on this computer only, in the project's .env file (never sent anywhere else)."""
    from dotenv import set_key
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        open(path, "a").close()
    set_key(path, config.EARTHDATA_USER_ENV, user)
    set_key(path, config.EARTHDATA_PASS_ENV, password)
    os.environ[config.EARTHDATA_USER_ENV] = user
    os.environ[config.EARTHDATA_PASS_ENV] = password


def forget_credentials():
    from dotenv import unset_key
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        unset_key(path, config.EARTHDATA_USER_ENV)
        unset_key(path, config.EARTHDATA_PASS_ENV)
    os.environ.pop(config.EARTHDATA_USER_ENV, None)
    os.environ.pop(config.EARTHDATA_PASS_ENV, None)
