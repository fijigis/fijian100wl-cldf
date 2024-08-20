import re

import pandas as pd
from pycldf import StructureDataset
from pyproj import Proj

orig_path = "data/AllVillages_Prov_Joined_XY_UTM60_18Mar2024.xlsx"

df = pd.read_excel(orig_path, header=0)

pj = Proj("+proj=utm +zone=60 +south +datum=WGS84 +units=m +no_defs +type=crs")

languages = []
id2language = {}
for index, row in df.iterrows():
    lon, lat = pj(float(row["POINT_X"]), float(row["POINT_Y"]), inverse=True)
    obj = {
        "ID": index,
        "Name": row["Village_Name_Only"].replace(" ", ""),
        "Communalect": row["Communalect"],
        "CommunalectGroup": row["ComGroupFeb2019"],
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
        "Village_Name_Only",
        "Communalect",
        "ComGroupFeb2019",
        "ComCode",
        "ComCG",
        "NAME",
        "DIVISION",
        "Status",
        "Status2",
        "Count",
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
    # assert row["VillagesComCodes_Name"] == id2language[language_id]["Name"]
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
