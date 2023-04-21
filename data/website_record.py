# Load data from DB
import os
from functools import partial

from tqdm.contrib.concurrent import process_map

import config
from utils import get_collection, get_text_from_html, load_json_from, save_json_to


def handle_chunk(
    begin: int,
    *,
    lang: str = "Engilsh",
    chunksize: int = 100,
):
    coll = get_collection(
        db_name=config.WEBSITE_DB_NAME, coll_name=config.WEBSITE_COLL_NAME
    )
    cursor = coll.aggregate(
        [
            {
                "$match": {
                    "content": {"$exists": True, "$ne": ""},
                    "language": {"$eq": lang},
                }
            },
            {"$skip": begin},
            {"$limit": chunksize},
        ]
    )
    results = []
    for doc in cursor:
        print("abc")
        # record only text and url
        text = get_text_from_html(doc["content"])
        if not text or text.startswith("<?xml"):
            continue
        results.append({"text": text, "url": doc["url"], "lang": doc["language"]})
    return results


def fetch_website_records(
    *,
    lang: str = "English",
    begin: int = 0,
    count: int = 20000,
    chunksize: int = 100,
):
    chunks_begin = list(range(begin, count, chunksize))
    # multi processing and show progress bar
    records = process_map(
        partial(handle_chunk, lang=lang, chunksize=chunksize),
        chunks_begin,
        max_workers=config.MAX_WORKERS,
        chunksize=1,
    )
    records = [item for rlist in records for item in rlist]
    return records


def get_website_records():
    # load website records from remote or local
    if not os.path.exists(config.WEBSITE_SAVE_PATH):
        print("fetching website records from DB...")
        records = fetch_website_records(lang="English", count=20000)
        save_json_to(config.WEBSITE_SAVE_PATH, records)
    else:
        print("loading website records from local...")
        records = load_json_from(config.WEBSITE_SAVE_PATH)
    return records
