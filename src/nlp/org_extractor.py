from typing import List

import spacy
from thefuzz import fuzz

import config


class OrganizationExtractor:
    def __init__(self, *, langs: List[str] = ["en", "zh"]):
        self.langs = langs
        self.load_models()

    # load model of selected langs
    def load_models(self):
        spacy.prefer_gpu(config.GPU_ID)
        if "en" in self.langs:
            self.nlp_en_trf = spacy.load("en_core_web_trf")
            self.nlp_en_train = spacy.load(config.ORG_EXTRACT_EN_MODEL)
        if "zh" in self.langs:
            self.nlp_zh_trf = spacy.load("zh_core_web_trf")
            self.nlp_zh_train = spacy.load(config.ORG_EXTRACT_ZH_MODEL)

    def get_models_of_lang(self, lang: str) -> List[spacy.Language]:
        if lang not in self.langs:
            raise "model of given lang not loaded"
        return (
            (self.nlp_en_trf, self.nlp_en_train)
            if lang == "en"
            else (self.nlp_zh_trf, self.nlp_zh_train)
        )

    def extract_org_from_text(self, text: str, lang: str) -> List[str]:
        """
        Extract organization from text
        The function use two models to increase the acc of extraction
        """

        nlp_trf, nlp_train = self.get_models_of_lang(lang)

        # model train by self
        doc_train = nlp_train(text)
        orgs_train = [ent.text for ent in doc_train.ents if ent.label_ == "ORG"]
        # model provide by spacy
        doc_trf = nlp_trf(text)
        orgs_trf = [ent.text for ent in doc_trf.ents if ent.label_ == "ORG"]

        # select ans from self training model
        orgs = list(set(orgs_train))

        # calc similarity of two org name
        def get_fuzz_ratio(org_1, org_2):
            mark = fuzz.partial_ratio(org_1, org_2)
            return mark if mark > 80 else 0

        # the more appear in the org list from spacy model, the higher mark
        def get_mark(o):
            return sum([get_fuzz_ratio(o, ot) for ot in orgs_trf]) + len(o)

        # sort by mark, the last one is highest
        orgs.sort(key=get_mark)

        # only trust when mark > 80
        org = orgs[-1] if len(orgs) and get_mark(orgs[-1]) >= 80 else None

        return org
