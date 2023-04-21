import pandas as pd

from utils import get_collection


# org list from schema, not using now
def fetch_org_list():
    # get collection from database
    coll = get_collection(db_name="datastore", coll_name="DDE_Schema_cruise")
    org_list = []
    # filter only documents with non-empty "org" field
    cursor = coll.find({"org": {"$exists": True, "$type": "array", "$ne": []}})
    # get all orgs
    for doc in cursor:
        org_list += doc["org"]
    # remove duplicates
    org_list = list(set(org_list))
    return org_list


# org list from org_simp table
def get_org_list():
    # load organization list
    orgs = pd.read_excel("files/org_simp.xlsx")
    orgs_full = list(orgs["org_name"])
    orgs_simp = list(orgs["org_name_simp"].dropna())
    orgs_all = orgs_full + orgs_simp
    orgs_all.sort(key=len, reverse=True)

    return orgs_all
