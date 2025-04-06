# immigration_data/merge_clean.py

import pandas as pd
import os
import glob

def load_and_clean_data(input_folder: str) -> pd.DataFrame:
    excel_fs = glob.glob(os.path.join(input_folder, "*.xls"))
    imm = []

    for fp in excel_fs:
        yearndreg = pd.read_excel(fp, nrows=5, header=None, engine="xlrd")
        year_text = yearndreg.iloc[0, 0]
        year = "".join(filter(str.isdigit, str(year_text)))
        region_text = yearndreg.iloc[3, 0]
        region = region_text.split(":")[-1].strip()

        df = pd.read_excel(fp, skiprows=5, engine="xlrd")
        witheld = df[df.iloc[:, 0].str.contains(r"\bData withheld\b", case=False, na=False, regex=True)].index.min()
        if pd.notna(witheld):
            df = df.iloc[:witheld]

        df["Year"] = year
        df["Region"] = region
        imm.append(df)

    opd = pd.concat(imm, ignore_index=True)
    df = opd.dropna(how='all')
    df = df[df["Characteristic"] != "No occupation/not working outside home"]

    # Initialize Grouping Columns
    df["Group"] = None
    df["Subgroup"] = None

    # Group Assignment Logic
    def get_index(val): return df[df["Characteristic"] == val].index[0] + 1

    total_start = get_index("Total")
    age_start = get_index("Age")
    marital_status_start = get_index("Marital status")
    occupation_start = get_index("Occupation")
    broad_class_start = get_index("Broad class of admission")
    leading_states_start = get_index("Leading states/territories of residence")

    df.loc[total_start:age_start-2, "Group"] = "Total"
    df.loc[age_start:marital_status_start-2, "Group"] = "Age"
    df.loc[marital_status_start:occupation_start-2, "Group"] = "Marital Status"
    df.loc[occupation_start:broad_class_start-2, "Group"] = "Occupation"
    df.loc[broad_class_start:leading_states_start-2, "Group"] = "Broad Class of Admission"
    df.loc[leading_states_start:, "Group"] = "Leading States"

    df["Subgroup"] = df["Characteristic"]
    df = df[df["Group"].notna()]

    df.drop(columns=["Characteristic"], inplace=True)
    df = df.dropna(subset=["Total", "Male", "Female"])

    return df
