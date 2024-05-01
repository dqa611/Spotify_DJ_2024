# Description: Install packages if not already installed
import importlib
import subprocess
import sys

# %%
# Import or install packages


def import_or_install_packages():
    packages = [
        "plotly",
        "sklearn",
        "importlib",
        "json",
        "math",
        "matplotlib",
        "numpy",
        "os",
        "pandas",
        "re",
        "seaborn",
        "urllib",
        "spotipy",
        "ipywidgets",
    ]
    for package in packages:
        try:
            importlib.import_module(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            importlib.import_module(package)
