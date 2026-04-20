from pathlib import Path
import re

import pandas as pd
from cldfbench import Dataset, CLDFSpec
from pyproj import Proj


NONCONCEPTS = {
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
}

COMMENTS = [
    "The first item",
    "The second item",
    "The third item",
    "The fourth item",
]


class Fijian100WLDataset(Dataset):
    dir = Path(__file__).parent
    id = "fijian100wl"

    def cldf_specs(self):
        return CLDFSpec(
            module="StructureDataset",
            dir=self.cldf_dir,
            metadata_fname="cldf-metadata.json",
        )

    def cmd_makecldf(self, args):
        df = pd.read_excel(
            self.raw_dir / "AllVillages_Prov_Joined_XY_UTM60_18Mar2024.xlsx",
            header=0,
        )
        pj = Proj("+proj=utm +zone=60 +south +datum=WGS84 +units=m +no_defs +type=crs")

        languages = []
        concepts = []
        values = []

        for index, row in df.iterrows():
            lon, lat = pj(float(row["POINT_X"]), float(row["POINT_Y"]), inverse=True)
            languages.append(
                {
                    "ID": index,
                    "Name": row["Village_Name_Only"].replace(" ", ""),
                    "Communalect": row["Communalect"],
                    "CommunalectGroup": row["ComGroupFeb2019"],
                    "Macroarea": "Papunesia",
                    "Latitude": lat,
                    "Longitude": lon,
                }
            )

        for cname in df.columns.tolist():
            if cname in NONCONCEPTS:
                continue
            fname, ename = cname.rstrip("_").split("__", 1)
            fname = fname.replace("_", " ")
            ename = ename.replace("_", " ")
            concepts.append(
                {
                    "ID": len(concepts),
                    "Name": cname,
                    "Description": f"Standard Fijian: {fname} ({ename})",
                }
            )

        for language_id, row in df.iterrows():
            for concept in concepts:
                entry = row[concept["Name"]]
                if pd.isna(entry):
                    continue

                entry = re.sub(r"\s+", " ", entry)
                entry = re.sub(r"^\s+", "", entry)
                entry = re.sub(r"\s+$", "", entry)
                if len(entry) <= 0:
                    continue

                words = re.split(r"[\n,]", entry)
                words = [re.sub(r"^\s+", "", x) for x in words]
                words = [re.sub(r"\s+", "", x) for x in words]

                if len(words) <= 1:
                    values.append(
                        {
                            "ID": len(values),
                            "Language_ID": language_id,
                            "Parameter_ID": concept["ID"],
                            "Value": words[0],
                        }
                    )
                else:
                    for i, word in enumerate(words):
                        values.append(
                            {
                                "ID": len(values),
                                "Language_ID": language_id,
                                "Parameter_ID": concept["ID"],
                                "Value": word,
                                "Comment": COMMENTS[i],
                            }
                        )

        args.writer.cldf.add_component(
            "LanguageTable",
            "Communalect",
            "CommunalectGroup",
        )
        args.writer.cldf.add_component("ParameterTable")

        args.writer.objects["LanguageTable"] = languages
        args.writer.objects["ParameterTable"] = concepts
        args.writer.objects["ValueTable"] = values
