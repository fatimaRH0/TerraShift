"""
earthdata.py - NASA Earthdata login helpers.

Most NASA satellite data needs a FREE Earthdata account:
    https://urs.earthdata.nasa.gov/users/new
"""

import getpass
import os
from urllib.parse import urlparse

import requests

from src import config

URS_HOST = "urs.earthdata.nasa.gov"


def get_credentials(ask=True):
    """Read the Earthdata username/password from the environment or from the .env file
    of the project (written once), or ask in the terminal when ask=True."""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    except ImportError:
        pass
    user = os.environ.get(config.EARTHDATA_USER_ENV)
    password = os.environ.get(config.EARTHDATA_PASS_ENV)
    if not (user and password):
        # Online deployment (e.g. Streamlit Community Cloud): the owner puts the account in the
        # app's Secrets, never in the code. Every visitor then gets the data without an account.
        try:
            import streamlit as st
            user = user or st.secrets.get(config.EARTHDATA_USER_ENV)
            password = password or st.secrets.get(config.EARTHDATA_PASS_ENV)
        except Exception:
            pass
    if ask and not user:
        user = input("Earthdata username: ").strip()
    if ask and not password:
        password = getpass.getpass("Earthdata password (hidden): ")
    return user, password


class EarthdataSession(requests.Session):
    """
    A requests Session that keeps the login when NASA redirects
    to urs.earthdata.nasa.gov and back (official NASA recipe).
    """

    def __init__(self, user, password):
        super().__init__()
        self.auth = (user, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        if "Authorization" in headers:
            original = urlparse(response.request.url).hostname
            redirect = urlparse(prepared_request.url).hostname
            if original != redirect and URS_HOST not in (original, redirect):
                del headers["Authorization"]
