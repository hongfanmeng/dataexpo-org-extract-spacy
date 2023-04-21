# general settings
MAX_WORKERS = 20
GPU_ID = 0
DB_CONN_STR = "mongodb://readonly:readonly@10.10.10.10:27017"

# config of fetching website records
WEBSITE_DB_NAME = "dataexpo"
WEBSITE_COLL_NAME = "network_cruise"
WEBSITE_SAVE_PATH = "json/website_records.json"

# config of org extract
# the core_web_trf model also use in the code
ORG_EXTRACT_ZH_MODEL = "models/50k-zh/model-best"
ORG_EXTRACT_EN_MODEL = "models/50k-en/model-best"
