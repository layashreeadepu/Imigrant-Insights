import pandas as pd
import os
import glob

ffpt = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS"
opf = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Mergefn/merged_output.xlsx"

excel_fs = glob.glob(os.path.join(ffpt, "*.xls"))

# Initialize empty list to store dataframes
imm = []

for fp in excel_fs:
    
    yearndreg = pd.read_excel(fp, nrows=5, header=None, engine="xlrd")  
    year_text = yearndreg.iloc[0, 0]
    #print(year_text)
    year = "".join(filter(str.isdigit, str(year_text))) 
    #print(year)
    region_text = yearndreg.iloc[3, 0]
    #print(region_text)
    region = region_text.split(":")[-1].strip() 
    #print(region)
    df = pd.read_excel(fp, skiprows=5, engine="xlrd")

    witheld = df[df.iloc[:, 0].str.contains(r"\bData withheld\b", case=False, na=False, regex=True)].index.min()
    #print(witheld)
    if pd.notna(witheld):  
        df = df.iloc[:witheld]
    
    df["Year"] = year
    df["Region"] = region
    
    imm.append(df)

# Merge all tables
print(imm)
opd = pd.concat(imm, ignore_index=True)
#opd.to_excel(opf, index=False)

#split of subgroups
#df = pd.read_excel(opf)
df = opd
df = df.dropna(how='all')
df = df[df["Characteristic"] != "No occupation/not working outside home"]
# Initialize columns for Group and Subgroup
df["Group"] = None
df["Subgroup"] = None

# Define ranges for each group based on the structure of the table
total_start = df[df["Characteristic"] == "Total"].index[0] + 1
age_start = df[df["Characteristic"] == "Age"].index[0] + 1
marital_status_start = df[df["Characteristic"] == "Marital status"].index[0] + 1
occupation_start = df[df["Characteristic"] == "Occupation"].index[0] + 1
broad_class_start = df[df["Characteristic"] == "Broad class of admission"].index[0] + 1
leading_states_start = df[df["Characteristic"] == "Leading states/territories of residence"].index[0] + 1

# Assign Group and Subgroup columns based on ranges
df.loc[total_start:age_start-2, "Group"] = "Total"
df.loc[total_start:age_start-2, "Subgroup"] = df.loc[total_start:age_start-2, "Characteristic"]

df.loc[age_start:marital_status_start-2, "Group"] = "Age"
df.loc[age_start:marital_status_start-2, "Subgroup"] = df.loc[age_start:marital_status_start-2, "Characteristic"]

df.loc[marital_status_start:occupation_start-2, "Group"] = "Marital Status"
df.loc[marital_status_start:occupation_start-2, "Subgroup"] = df.loc[marital_status_start:occupation_start-2, "Characteristic"]

df.loc[occupation_start:broad_class_start-2, "Group"] = "Occupation"
df.loc[occupation_start:broad_class_start-2, "Subgroup"] = df.loc[occupation_start:broad_class_start-2, "Characteristic"]

df.loc[broad_class_start:leading_states_start-2, "Group"] = "Broad Class of Admission"
df.loc[broad_class_start:leading_states_start-2, "Subgroup"] = df.loc[broad_class_start:leading_states_start-2, "Characteristic"]

df.loc[leading_states_start:, "Group"] = "Leading States"
df.loc[leading_states_start:, "Subgroup"] = df.loc[leading_states_start:, "Characteristic"]

# Filter out rows that are not part of any group (e.g., Total rows)
df = df[df["Group"].notna()]

# Drop the original 'Characteristic' column if no longer needed
df.drop(columns=["Characteristic"], inplace=True)
df.columns
df = df.dropna(how='all')
df = df.dropna(subset=['Total', 'Male', 'Female'])
df.to_excel(opf, index=False)
