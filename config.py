# config.py

import os, yaml, logging
from dotenv import load_dotenv
from google.cloud import firestore, secretmanager
import google.auth

load_dotenv()  # подгружает .env

# Инициализация базового логгера до полной настройки, если он нужен рано
_temp_logger = logging.getLogger('ConfigInit')
_temp_logger.setLevel(logging.INFO)
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
if not _temp_logger.handlers:
    _temp_logger.addHandler(_ch)

ENV = os.getenv("APP_ENV", "production").lower()
GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

def get_secret(secret_id, version_id="latest"):
    if not GCP_PROJECT_ID:
        _temp_logger.warning("GOOGLE_CLOUD_PROJECT is not set. Cannot fetch secrets from Secret Manager.")
        return None
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GCP_PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    try:
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        _temp_logger.info(f"Successfully fetched secret '{secret_id}' from Secret Manager.")
        return secret_value
    except Exception as e:
        _temp_logger.error(f"Failed to access secret '{secret_id}' from Secret Manager: {e}")
        return None

class Config:
    def __init__(self, config_path='configs/config.yaml'):
        cfg_file = os.path.join(os.path.dirname(__file__), config_path)
        if os.path.exists(cfg_file):
            with open(cfg_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            _temp_logger.info(f"Configuration loaded from {cfg_file}")
        else:
            _temp_logger.error(f"Configuration file {cfg_file} not found.")
            self.config = {}

        # Load sensitive keys
        self.openai_api_key = None
        self.cryptocompare_api_key = None

        if ENV == "production" and GCP_PROJECT_ID:
            _temp_logger.info("Production environment detected, attempting to load secrets from Google Secret Manager.")
            self.openai_api_key = get_secret("OPENAI_API_KEY")
            self.cryptocompare_api_key = get_secret("CRYPTOCOMPARE_API_KEY")
        
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if self.openai_api_key:
                 _temp_logger.info("Loaded OPENAI_API_KEY from environment variable.")
            else:
                _temp_logger.warning("OPENAI_API_KEY not found in Secret Manager or environment variables.")

        if not self.cryptocompare_api_key:
            self.cryptocompare_api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
            if self.cryptocompare_api_key:
                _temp_logger.info("Loaded CRYPTOCOMPARE_API_KEY from environment variable.")
            else:
                _temp_logger.warning("CRYPTOCOMPARE_API_KEY not found in Secret Manager or environment variables.")


    def get(self, section, key, default=None):
        # Prioritize specific sensitive keys if requested
        if section == "api_keys":
            if key == "openai":
                return self.openai_api_key or default
            if key == "cryptocompare":
                return self.cryptocompare_api_key or default
        return self.config.get(section, {}).get(key, default)

config_instance = Config() # Renamed to avoid conflict with module name
SNAPSHOT_ENABLED = (os.getenv("SNAPSHOT_ENABLED","false").lower()=="true") or ENV in ("development","local")

def setup_logging(cfg_instance): # Pass instance
    logger = logging.getLogger('ChartGenius2')
    if not logger.handlers: # Ensure handlers are not duplicated
        log_level_str = cfg_instance.get('logging','level','INFO')
        log_format_str = cfg_instance.get('logging','format','%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        logger.setLevel(getattr(logging, log_level_str.upper(), logging.INFO))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(log_format_str))
        logger.addHandler(ch)
    return logger

logger = setup_logging(config_instance) # Use renamed instance

# Update get_firestore_client to use the new logger
def get_firestore_client():
    try:
        creds, effective_project_id = google.auth.default()
        # Use GCP_PROJECT_ID if set, otherwise the one from google.auth.default()
        project_to_use = GCP_PROJECT_ID or effective_project_id
        if not project_to_use:
            logger.error("Google Cloud project ID could not be determined. Firestore client not initialized.")
            return None
        logger.info(f"Initializing Firestore client for project: {project_to_use}")
        return firestore.Client(credentials=creds, project=project_to_use)
    except Exception as e:
        logger.error(f"Error initializing Firestore: {e}", exc_info=True)
        return None

db = get_firestore_client()

# Make keys directly accessible if needed, e.g. by other modules directly importing them
OPENAI_API_KEY = config_instance.openai_api_key
CRYPTOCOMPARE_API_KEY = config_instance.cryptocompare_api_key
