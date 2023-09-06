"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""


import logging
import colorlog
from dotenv import load_dotenv
import os


def setup_logger(context):
    """Return a logger with a default ColoredFormatter."""
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(reset)s %(blue)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    logger = logging.getLogger(context)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


logger = setup_logger(__name__)


def get_db_credentials():
    DB_PASSWORD, DB_SERVER, DB_SECRET_KEY = None, None, None
    DB_USERNAME, DB_DRIVER, DB_DATABASE = None, None, None

    load_dotenv()
    DB_USERNAME = os.environ.get("DBUSERNAME")
    DB_PASSWORD = os.environ.get("DBPASSWORD")
    DB_SERVER = os.environ.get("DBSERVER")
    DB_DRIVER = os.environ.get("DBDRIVER")
    DB_DATABASE = os.environ.get("DBDATABASE")
    DB_SECRET_KEY = os.environ.get("DBSECRETKEY")

    return DB_PASSWORD, DB_SERVER, DB_USERNAME, DB_DRIVER, DB_DATABASE, DB_SECRET_KEY


def get_api_credentials():
    OPENAIAPIKEY, AZURE_OPENAIKEY, AZURE_ENDPOINT, PERSONAL_KEY = None, None, None, None

    load_dotenv()
    OPENAIAPIKEY = os.environ.get("OPENAIAPIKEY")
    AZURE_OPENAIKEY = os.environ.get("AZOPENAIAPIKEY")
    AZURE_ENDPOINT = os.environ.get("AZENDPOINT")
    PERSONAL_KEY = os.environ.get("PERSONALKEY")

    return OPENAIAPIKEY, AZURE_OPENAIKEY, AZURE_ENDPOINT, PERSONAL_KEY
