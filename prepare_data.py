import re
import textwrap
from functools import partial

import spacy
from spacy.tokens import DocBin
from tqdm.contrib.concurrent import process_map

import config
from data import get_org_list, get_website_records
from utils import get_automaton, get_words_in_text, split_train_dev

# text will be split to multi part if it is too long
# max text length of each part
MAX_TEXT_CHUNK_LEN = 500
# max text length of text of one record
MAX_TEXT_TOTAL_LEN = 100000

TRAIN_DATA_SIZE = 40000
DEV_DATA_SIZE = 10000


def find_orgs(automation, record):
    results = []
    text = record["text"]

    # find orgs from text
    orgs_text = get_words_in_text(automation, text)
    orgs_text.sort(key=len, reverse=True)

    # using textwrap to split text to chunks
    text_list = textwrap.wrap(text, MAX_TEXT_CHUNK_LEN)
    max_block_count = MAX_TEXT_TOTAL_LEN // MAX_TEXT_CHUNK_LEN

    # if text is too long, only keep the first and last parts
    if len(text_list) > max_block_count:
        half = max_block_count // 2
        text_list = text_list[:half] + text_list[-half:]

    # find org in each part
    for text in text_list:
        entities = []
        for org in orgs_text:
            # find all org from text
            for match in re.finditer(f" {re.escape(org)} ", text):
                ent = (match.start() + 1, match.end() - 1, "ORG")
                # check if overlap
                if any((e[0] <= ent[1] and ent[0] <= e[1]) for e in entities):
                    continue
                entities.append(ent)
        # ignore if no org
        if entities == []:
            continue

        results.append((text, entities))

    return results


def mark_org_in_records(records, orgs_all):
    with open("files/words_alpha.txt", "r") as f:
        valid_words = list(set(f.read().split()))

    # blacklist the org that are not valid
    # WARN: remove the following organizations if they are likely to be the answer
    blacklist = ["google", "twitter", "facebook", "linkedin", "intel", "microsoft"]

    # find words not in blacklist and valid_words
    # using automaton to speed up
    automaton = get_automaton(valid_words + blacklist)
    orgs_to_search = list(
        filter(lambda o: len(o) >= 4 and f" {o.lower()} " not in automaton, orgs_all)
    )
    automaton_all = get_automaton(orgs_to_search)

    print("finding orgs in text...")
    # find orgs from each text
    results = process_map(
        partial(find_orgs, automaton_all),
        records,
        max_workers=config.MAX_WORKERS,
        chunksize=1000,
    )
    results = [item for r in results if r for item in r]

    return results


def handle_sample(sample):
    nlp = spacy.blank("en")
    text, annotations = sample
    doc = nlp(text)
    ents = []
    for start, end, label in annotations:
        span = doc.char_span(start, end, label=label)
        ents.append(span)
    doc.ents = ents
    return doc


def convert_to_docbin(data):
    db = DocBin()
    doc_list = process_map(
        handle_sample, data, max_workers=config.MAX_WORKERS, chunksize=100
    )
    for doc in doc_list:
        db.add(doc)
    return db


def get_train_dev_data(training_data):
    train_data, dev_data = split_train_dev(training_data)
    print("generating train data...")
    db_train = convert_to_docbin(train_data[:TRAIN_DATA_SIZE])
    print("generating dev data...")
    db_dev = convert_to_docbin(dev_data[:DEV_DATA_SIZE])

    return db_train, db_dev


if __name__ == "__main__":
    records = get_website_records()
    orgs_all = get_org_list()
    results = mark_org_in_records(records, orgs_all)

    db_train, db_dev = get_train_dev_data(results)
    db_train.to_disk("files/train_40k.spacy")
    db_dev.to_disk("files/dev_10k.spacy")
