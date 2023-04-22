# Load data from DB
from datetime import datetime

import pandas as pd
from tqdm import tqdm

import config
from nlp import OrganizationExtractor
from utils import get_collection, get_text_from_html

if __name__ == "__main__":
    coll = get_collection(
        db_name=config.WEBSITE_DB_NAME, coll_name=config.WEBSITE_COLL_NAME
    )

    df = pd.read_excel("files/input.xlsx")

    records = []
    print("loading data from DB...")
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        doc = coll.find_one({"url": row["url"]})
        text = get_text_from_html(doc["content"])
        if not text or text.startswith("<?xml"):
            continue
        if doc["language"] != "English":
            continue
        records.append(
            {
                "text": text,
                "url": doc["url"],
                "language": doc["language"],
            }
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
