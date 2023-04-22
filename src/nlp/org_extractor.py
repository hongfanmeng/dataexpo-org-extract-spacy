from typing import List

import spacy
from thefuzz import fuzz

import config
from data import get_org_list
from utils import get_automaton

MAX_TEXT_LEN = 10000


class OrganizationExtractor:
    def __init__(self, *, langs: List[str] = ["en", "zh"]):
        self.langs = langs
        orgs_prior = get_org_list()
        self.automaton_prior = get_automaton(orgs_prior)
        self.load_models()

    # load model of selected langs
    def load_models(self):
        spacy.prefer_gpu(config.GPU_ID)
        if "en" in self.langs:
            self.nlp_en_trf = spacy.load("en_core_web_trf")
            self.nlp_en_train = spacy.load(config.ORG_EXTRACT_EN_MODEL)
        if "zh" in self.langs:
            self.nlp_zh_trf = spacy.load("zh_core_web_trf")
            # NO chinese self trainning model now

    def get_models_of_lang(self, lang: str) -> List[spacy.Language]:
        if lang not in self.langs:
            raise "model of given lang not loaded"
        return (
            (self.nlp_en_trf, self.nlp_en_train)
            if lang == "en"
            else (self.nlp_zh_trf, None)
        )

    def extract_org_from_text(self, text: str, lang: str) -> List[str]:
        """
        Extract organization from text
        The function use two models to increase the acc of extraction
        """

        if len(text) > MAX_TEXT_LEN:
            half = MAX_TEXT_LEN // 2
            text = text[:half] + text[-half:]

        nlp_trf, nlp_train = self.get_models_of_lang(lang)

        # model train by self
        if nlp_train:
            doc_train = nlp_train(text)
            orgs_train = [ent.text for ent in doc_train.ents if ent.label_ == "ORG"]

        # model provide by spacy
        doc_trf = nlp_trf(text)
        orgs_trf = [ent.text for ent in doc_trf.ents if ent.label_ == "ORG"]

        # select ans from self trainning model
        # if not self trainning model, select ans from trf model
        orgs = list(set(orgs_train)) if nlp_train else list(set(orgs_trf))

        # calc similarity of two org name
        def cutoff(mark, cutoff_val=80):
            return mark if mark > cutoff_val else 0

        # the more appear in the org list from spacy model, the higher mark
        def get_mark(org):
            mark = sum(
                [cutoff(fuzz.partial_ratio(org, org_trf)) for org_trf in orgs_trf]
            )
            # if not self trainning model, ans select form orgs_trf at least 100
            # so mark should minus 100
            if not nlp_train:
                mark -= 100
            # mark from prior org list
            mark += 1000 if org in self.automaton_prior else 0
            return mark

        # sort by mark, the last one is highest
        orgs.sort(key=get_mark)

        # only trust when mark > 80
        org = orgs[-1] if len(orgs) and get_mark(orgs[-1]) >= 80 else None

        return org
