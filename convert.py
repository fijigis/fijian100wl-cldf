import re

import pandas as pd
from pycldf import StructureDataset

orig_path = "data/Fiji100WL_Feb2020_GCS_TableToExcel.xlsx"

df = pd.read_excel(orig_path, header=0)

languages = []
id2language = {}
for index, row in df.iterrows():
    lon, lat = float(row["POINT_X"]), float(row["POINT_Y"])
    obj = {
        "ID": index,
        "Name": row["VillagesComCodes_Name"],
        "Communalect": None if pd.isna(row["Communalect"]) else row["Communalect"],
        "CommunalectGroup": None
        if pd.isna(row["CommunlectGroup"])
        else row["CommunlectGroup"],  # typo in the sheet
        "Macroarea": "Papunesia",
        "Latitude": lat,
        "Longitude": lon,
    }
    languages.append(obj)
    id2language[obj["ID"]] = obj

concepts = []
id2concept = {}
nonconcepts = set(
    [
        "OBJECTID_1",
        "VillagesComCodes_Name",
        "VillagesComCodes_Tikina_Makawa",
        "VillagesComCodes_PROVINCE",
        "ComCodeGrps_Communalect",
        "ComGroupFeb2019",
        "ComComGroup",
        "CCODE",
        "CGCODE",
        "Com_ComGroup",
        "Communalect",
        "CommunlectGroup",  # typo in the sheet
        "CCODE_1",
        "POINT_X",
        "POINT_Y",
    ]
)

for cname in df.columns.tolist():
    if cname in nonconcepts:
        continue
    fname, ename = cname.rstrip("_").split("__", 1)
    fname = fname.replace("_", " ")
    ename = ename.replace("_", " ")
    obj = {
        "ID": len(concepts),
        "Name": cname,
        "Description": "Standard Fijian: {} ({})".format(fname, ename),
    }
    concepts.append(obj)
    id2concept[obj["ID"]] = obj

values = []
for language_id, row in df.iterrows():
    assert row["VillagesComCodes_Name"] == id2language[language_id]["Name"]
    for concept in concepts:
        entry = row[concept["Name"]]
        if pd.isna(entry):
            continue
        entry = re.sub(r"\s+", " ", entry)
        entry = re.sub(r"^\s+", "", entry)
        entry = re.sub(r"\s+$", "", entry)
        if len(entry) <= 0:
            continue
        words = re.split(r"[\n\,]", entry)
        words = list(map(lambda x: re.sub(r"^\s+", "", x), words))
        words = list(map(lambda x: re.sub(r"\s+", "", x), words))
        if len(words) <= 1:
            word = words[0]
            obj = {
                "ID": len(values),
                "Language_ID": language_id,
                "Parameter_ID": concept["ID"],
                "Value": word,
            }
            values.append(obj)
        else:
            comments = [
                "The first item",
                "The second item",
                "The third item",
                "The fourth item",
            ]
            for i, word in enumerate(words):
                obj = {
                    "ID": len(values),
                    "Language_ID": language_id,
                    "Parameter_ID": concept["ID"],
                    "Value": word,
                    "Comment": comments[i],
                }
                values.append(obj)

dbname = "fijian100wl"
dataset = StructureDataset.in_dir(dbname)
dataset.add_component(
    "LanguageTable",
    "Communalect",
    "CommunalectGroup",
)
dataset.add_component("ParameterTable")
dataset.write(
    ValueTable=values,
    ParameterTable=concepts,
    LanguageTable=languages,
)
