from datetime import datetime

import pandas as pd
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

import config
from nlp import OrganizationExtractor
from utils import get_client, get_collection, get_text_from_html

# using share client
client = get_client()


def get_data_from_db(url):
    coll_list = [
        get_collection(db_name="dataexpo", coll_name="top_website", client=client),
        get_collection(db_name="dataexpo", coll_name="network_cruise", client=client),
    ]
    # find from multi coll
    doc = next(
        (
            coll.find_one({"url": url})
            for coll in coll_list
            if coll.find_one({"url": url})
        ),
        "",
    )
    text = get_text_from_html(doc["content"])
    # skip xml files
    text = "" if text.startswith("<?xml") else text
    return {
        "text": text,
        "url": doc["url"],
        "language": doc["language"],
    }


if __name__ == "__main__":
    print("reading input...")
    df = pd.read_excel("files/input.xlsx")
    urls = list(df["url"])

    records = []

    print("loading data from DB...")
    records = process_map(
        get_data_from_db,
        urls,
        max_workers=config.MAX_WORKERS,
        chunksize=100,
    )

    # only english model train now
    org_extractor = OrganizationExtractor()
    results = []
    print("extracting organizatino from text...")
    for record in tqdm(records):
        lang = "zh" if record["language"] == "Chinese" else "en"
        org = org_extractor.extract_org_from_text(record["text"], lang=lang)
        results.append({"url": record["url"], "org": org})

    df = pd.DataFrame(results)
    now = datetime.now()
    filename = f"output/output-{now.strftime('%m-%d-%H-%M')}.xlsx"
    df.to_excel(filename)
