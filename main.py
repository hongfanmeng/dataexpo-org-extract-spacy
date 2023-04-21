# Load data from DB
import re
from datetime import datetime

import pandas as pd
from tqdm import tqdm

import config
from nlp import OrganizationExtractor
from utils import get_collection, get_text_from_html


def write_excel(df: pd.DataFrame, filename: str):
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    df.to_excel(writer, sheet_name="Sheet1", index=False)

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    text_wrap_format = workbook.add_format({"text_wrap": True})
    worksheet.set_column(0, 2, 50, text_wrap_format)

    writer.close()


if __name__ == "__main__":
    coll = get_collection(
        db_name=config.WEBSITE_DB_NAME, coll_name=config.WEBSITE_COLL_NAME
    )

    df = pd.read_excel("test_data.xlsx")

    records = []
    for index, row in tqdm(df.iterrows(), total=99):
        orgs_ans = re.split(r"\n|,", row["organization"])
        orgs_ans = list(map(lambda s: s.strip(), orgs_ans))
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
                "orgs_ans": orgs_ans,
            }
        )

    # only english model train now
    org_extractor = OrganizationExtractor(langs=["en"])
    results = []
    for record in records:
        lang = "zh" if record["language"] == "Chinese" else "en"
        org = org_extractor.extract_org_from_text(record["text"], lang=lang)
        results.append(
            {
                "url": record["url"],
                "org": org,
                "orgs_ans": "\n".join(record["orgs_ans"]),
            }
        )

    df = pd.DataFrame(results)
    now = datetime.now()
    filename = f"results-{now.strftime('%m-%d-%H-%M')}.xlsx"
    write_excel(df, filename)