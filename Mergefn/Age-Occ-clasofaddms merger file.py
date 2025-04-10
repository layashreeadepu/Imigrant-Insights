import pandas as pd
import os
import glob
import numpy as np

# Define file paths
input_folder_path = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/input dataset/all countries"
output_file_path = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Mergefn/occupation_age_admission_merged_updates.xlsx"

# Get all Excel files in the input directory
excel_files = glob.glob(os.path.join(input_folder_path, "*.xls"))

# Print how many files we found (for debugging)
print(f"Found {len(excel_files)} .xls files in the specified directory")

# Initialize empty list to store dataframes
all_dataframes = []

# Process each file
for file_path in excel_files:
    try:
        print(f"Processing file: {os.path.basename(file_path)}")
        
        # Extract year and region information
        metadata = pd.read_excel(file_path, nrows=5, header=None, engine="xlrd")  
        
        # Extract year from first row text
        year_text = metadata.iloc[0, 0]
        year = "".join(filter(str.isdigit, str(year_text)))
        
        # Extract region from the region row
        region_text = metadata.iloc[3, 0]
        region = region_text.split(":")[-1].strip()
        
        print(f"  - Year extracted: {year}, Region extracted: {region}")
        
        # Read the actual data
        df = pd.read_excel(file_path, skiprows=5, engine="xlrd")
        
        # Find and remove footer notes
        footer_indicators = ["Represents zero", "Data withheld", "Note:"]
        footer_idx = None
        
        for indicator in footer_indicators:
            try:
                idx = df[df.iloc[:, 0].str.contains(indicator, case=False, na=False, regex=True)].index.min()
                if pd.notna(idx):
                    if footer_idx is None or idx < footer_idx:
                        footer_idx = idx
            except (AttributeError, TypeError):
                continue
        
        if pd.notna(footer_idx):
            df = df.iloc[:footer_idx]
        
        # Add year and region columns
        df["Year"] = year
        df["Region"] = region
        
        # Store the dataframe
        all_dataframes.append(df)
        print(f"  - Successfully processed with {len(df)} rows")
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

# Check if we have dataframes to merge
if len(all_dataframes) == 0:
    print("No data was successfully processed. Check the file paths and file format.")
else:
    # Merge all tables
    print(f"Merging {len(all_dataframes)} dataframes...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"Merged dataframe has {len(merged_df)} rows")
    
    # Clean the data
    merged_df = merged_df.dropna(how='all')
    
    # Initialize columns for Group and Subgroup
    merged_df["Group"] = None
    merged_df["Subgroup"] = None
    
    # Process each year-region combination separately
    unique_combinations = merged_df[['Year', 'Region']].drop_duplicates().values
    
    for year, region in unique_combinations:
        subset = merged_df[(merged_df['Year'] == year) & (merged_df['Region'] == region)]
        
        # Find section indices within this subset
        try:
            age_rows = subset[subset["Characteristic"] == "Age"].index
            if len(age_rows) > 0:
                age_idx = age_rows[0]
                age_start = age_idx + 1
            else:
                age_idx = None
                age_start = None
        except:
            age_idx = None
            age_start = None
            
        try:
            occupation_rows = subset[subset["Characteristic"] == "Occupation"].index
            if len(occupation_rows) > 0:
                occupation_idx = occupation_rows[0]
                occupation_start = occupation_idx + 1
            else:
                occupation_idx = None
                occupation_start = None
        except:
            occupation_idx = None
            occupation_start = None
            
        try:
            # Look for either "Broad class of admission" or "Major class of admission"
            admission_rows = subset[
                subset["Characteristic"].str.contains("class of admission", case=False, na=False)
            ].index
            if len(admission_rows) > 0:
                admission_idx = admission_rows[0]
                admission_start = admission_idx + 1
            else:
                admission_idx = None
                admission_start = None
        except:
            admission_idx = None
            admission_start = None
        
        # Find the next section after each section to determine the end
        all_section_indices = sorted(
            [i for i in [age_idx, occupation_idx, admission_idx] if i is not None])
        
        # Assign Age group
        if age_idx is not None:
            # Find the next section after Age
            next_idx = min([i for i in all_section_indices if i > age_idx] + [subset.index.max() + 1])
            merged_df.loc[age_start:next_idx-1, "Group"] = "Age"
            merged_df.loc[age_start:next_idx-1, "Subgroup"] = merged_df.loc[age_start:next_idx-1, "Characteristic"]
        
        # Assign Occupation group
        if occupation_idx is not None:
            # Find the next section after Occupation
            next_idx = min([i for i in all_section_indices if i > occupation_idx] + [subset.index.max() + 1])
            merged_df.loc[occupation_start:next_idx-1, "Group"] = "Occupation"
            merged_df.loc[occupation_start:next_idx-1, "Subgroup"] = merged_df.loc[occupation_start:next_idx-1, "Characteristic"]
        
        # Assign Broad Class of Admission group
        if admission_idx is not None:
            # Find the next section after Admission
            next_idx = min([i for i in all_section_indices if i > admission_idx] + [subset.index.max() + 1])
            merged_df.loc[admission_start:next_idx-1, "Group"] = "Broad Class of Admission"
            merged_df.loc[admission_start:next_idx-1, "Subgroup"] = merged_df.loc[admission_start:next_idx-1, "Characteristic"]
    
    # Filter the dataframe to keep only the sections we want
    filtered_df = merged_df[merged_df["Group"].isin(["Age", "Occupation", "Broad Class of Admission"])]
    
    # Drop rows with missing or invalid data
    filtered_df = filtered_df.dropna(subset=["Total", "Male", "Female"], how="all")
    
    # Handle data cleaning - replace "-" with NaN or 0 based on context
    for col in ["Total", "Male", "Female", "Unknown"]:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].replace("-", 0)
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")
    
    # Drop the original 'Characteristic' column as we now have Group and Subgroup
    if "Characteristic" in filtered_df.columns:
        filtered_df.drop(columns=["Characteristic"], inplace=True)
    
    # Output the refined dataset
    filtered_df.to_excel(output_file_path, index=False)
    
    print(f"Processing complete. Filtered data saved to {output_file_path}")
    print(f"Dataset contains {len(filtered_df)} rows with data from Age, Occupation, and Broad Class of Admission categories.")
    print(f"Data spans {len(filtered_df['Year'].unique())} years and {len(filtered_df['Region'].unique())} regions.")