# %%


from spotipy.oauth2 import SpotifyOAuth
import spotipy
import os

from QuocAnh_py.others.utilities import import_json


# %%


def import_credentials(path):
    credentials = import_json(path)

    USERNAME = credentials["USERNAME"]
    USERNAME_ID = credentials["USERNAME_ID"]
    CLIENT_ID = credentials["CLIENT_ID"]
    CLIENT_SECRET = credentials["CLIENT_SECRET"]
    REDIRECT_URI = credentials["REDIRECT_URI"]
    SCOPE = credentials["SCOPE"]

    return USERNAME, USERNAME_ID, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE


# %%


def run_spotify_api(CLIENT_ID: str, CLIENT_SECRET: str, REDIRECT_URI: str, SCOPE: str):

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
        )
    )
    return sp


# %%

path = os.getcwd()
cred_path = ".\\spotify_cred.json"
cred_path = "\\".join([path, cred_path])
if os.path.exists(cred_path):

    USERNAME, USERNAME_ID, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE = (
        import_credentials(cred_path)
    )

    sp = run_spotify_api(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)

else:
    raise ValueError("spotify_cred.json not found in the current directory.")
