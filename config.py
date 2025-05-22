# config.py

import os, yaml, logging
from dotenv import load_dotenv
from google.cloud import firestore
import google.auth

load_dotenv()  # подгружает .env

class Config:
    def __init__(self, config_path='configs/config.yaml'):
        temp = logging.getLogger('ConfigTemp')
        temp.setLevel(logging.INFO)
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        if not temp.handlers:
            temp.addHandler(h)
        cfg_file = os.path.join(os.path.dirname(__file__), config_path)
        if os.path.exists(cfg_file):
            with open(cfg_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            temp.info(f"Конфигурация загружена из {cfg_file}")
        else:
            temp.error(f"Файл конфигурации {cfg_file} не найден.")
            self.config = {}

    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)

config = Config()
ENV = os.getenv("APP_ENV", "production").lower()
SNAPSHOT_ENABLED = (os.getenv("SNAPSHOT_ENABLED","false").lower()=="true") or ENV in ("development","local")

def setup_logging(cfg):
    logger = logging.getLogger('ChartGenius2')
    if not logger.handlers:
        lvl = cfg.get('logging','level','INFO')
        fmt = cfg.get('logging','format','%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        logger.setLevel(getattr(logging, lvl.upper(), logging.INFO))
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(fmt))
        logger.addHandler(h)
    return logger

logger = setup_logging(config)

def get_firestore_client():
    try:
        creds, proj = google.auth.default()
        return firestore.Client(credentials=creds, project=proj)
    except Exception as e:
        logger.error(f"Ошибка инициализации Firestore: {e}")
        return None

db = get_firestore_client()
