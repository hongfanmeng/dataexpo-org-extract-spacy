import json
import random

import ahocorasick
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.collection import Collection

import config


def get_automaton(words):
    automaton = ahocorasick.Automaton()
    for index, word in enumerate(words):
        # match with space before and after
        automaton.add_word(f" {word} ", (index, word))
    automaton.make_automaton()
    return automaton


def get_words_in_text(automaton, text):
    return [word for _, (_, word) in automaton.iter(f" {text.strip()} ")]


def get_client(
    conn_str: str = config.DB_CONN_STR,
) -> MongoClient:
    return MongoClient(conn_str)


def get_collection(
    *, db_name: str, coll_name: str, client: MongoClient | None = None
) -> Collection:
    if client is None:
        client = get_client()
    db = client[db_name]
    coll = db[coll_name]
    return coll


def save_json_to(path: str, data: dict) -> None:
    with open(path, "w", encoding="UTF-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


def load_json_from(path: str) -> dict:
    with open(path, "r", encoding="UTF-8") as f:
        data = json.load(f)
    return data


def get_text_from_html(html: str) -> str:
    # some xml in DB
    parser = "lxml" if "<html" in html else "xml"
    soup = BeautifulSoup(html, features=parser)
    # kill all script and style elements
    for script in soup(["script", "style", "noscript"]):
        script.extract()  # rip it out

    # get text, seperate by ` `
    text = " ".join([" ".join(text.split()) for text in soup.stripped_strings])

    return text


def split_train_dev(data, radio=0.8, seed=42):
    data = data.copy()
    random.seed(seed)
    random.shuffle(data)
    size = len(data)
    sep = int(size * 0.8)
    train_data = data[:sep]
    dev_data = data[sep:]
    return train_data, dev_data
