import pandas as pd
import os
import glob
import numpy as np

# Define a function to standardize region names
def standardize_region_name(region):
    """
    Standardize region names to handle inconsistencies across different years
    """
    # Dictionary mapping variations to standardized names
    region_mapping = {
        # Variations for countries with "The" in their name
        "Bahamas": "Bahamas, The",
        "Bahamas, The": "Bahamas, The",
        "Gambia": "Gambia, The",
        "Gambia, The": "Gambia, The",
        
        # Countries that changed names
        "Czechia": "Czech Republic",
        "Czech Republic": "Czech Republic",
        
        "Eswatini": "Eswatini",
        "Eswatini (formerly Swaziland)": "Eswatini",
        "Swaziland": "Eswatini",
        
        "North Macedonia": "North Macedonia",
        "North Macedonia (formerly Macedonia)": "North Macedonia",
        "Macedonia": "North Macedonia",
        
        # British territories
        "Virgin Islands, British": "British Virgin Islands",
        "British Virgin Islands": "British Virgin Islands",
        
        # Variations with different formatting
        "China": "China",
        "China, People's Republic": "China",
        
        "Congo, Democratic Republic": "Congo, Democratic Republic of the",
        "Congo, Democratic Republic of the": "Congo, Democratic Republic of the",
        
        "Congo, Republic": "Congo, Republic of the",
        "Congo, Republic of the": "Congo, Republic of the",
        
        "Saint Kitts and Nevis": "Saint Kitts-Nevis",
        "Saint Kitts-Nevis": "Saint Kitts-Nevis",
    }
    
    # Return the standardized name if in the mapping, otherwise return the original
    return region_mapping.get(region, region)

# Define file paths
input_folder_path = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/input dataset/all countries"
output_file_path = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Mergefn/all.countries.merged.final.xls"

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
        
        # Standardize region names to handle inconsistencies
        region = standardize_region_name(region)
        
        print(f"  - Year extracted: {year}, Region extracted: {region} (standardized)")
        
        # Read the actual data
        df = pd.read_excel(file_path, skiprows=5, engine="xlrd")
        
        # Find and remove footer notes
        footer_indicators = ["Represents zero", "Data withheld", "Note:", "- Represents"]
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
            
        # Also identify the sections we want to explicitly exclude
        try:
            marital_rows = subset[
                subset["Characteristic"].str.contains("Marital", case=False, na=False)
            ].index
            if len(marital_rows) > 0:
                marital_idx = marital_rows[0]
                marital_start = marital_idx + 1
            else:
                marital_idx = None
                marital_start = None
        except:
            marital_idx = None
            marital_start = None
            
        try:
            states_rows = subset[
                subset["Characteristic"].str.contains("states of permanent residence", case=False, na=False) |
                subset["Characteristic"].str.contains("Leading states", case=False, na=False) |
                subset["Characteristic"].str.contains("Top 20 states", case=False, na=False)
            ].index
            if len(states_rows) > 0:
                states_idx = states_rows[0]
                states_start = states_idx + 1
            else:
                states_idx = None
                states_start = None
        except:
            states_idx = None
            states_start = None
        
        # Find the next section after each section to determine the end
        all_section_indices = sorted(
            [i for i in [age_idx, occupation_idx, admission_idx, marital_idx, states_idx] if i is not None])
        
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
    
    # Explicitly filter to keep only the sections we want
    filtered_df = merged_df[merged_df["Group"].isin(["Age", "Occupation", "Broad Class of Admission"])]
    
    # Remove "New arrivals" and "Adjustments of status" rows
    filtered_df = filtered_df[
        ~filtered_df["Subgroup"].str.contains("New arrivals", case=False, na=False) & 
        ~filtered_df["Subgroup"].str.contains("Adjustments of status", case=False, na=False)
    ]
    
    # Also filter out the "Total" rows that are at the start of the file (usually row 6)
    filtered_df = filtered_df[
        ~(filtered_df["Subgroup"] == "Total")
    ]
    
    # Print info about filtered rows
    print(f"Filtered dataframe has {len(filtered_df)} rows after removing unwanted sections and rows")
    
    # Drop rows with missing or invalid data
    filtered_df = filtered_df.dropna(subset=["Total", "Male", "Female"], how="all")
    
    # Handle data cleaning - replace "-" with 0 and "D" with region-specific means
    for col in ["Total", "Male", "Female", "Unknown"]:
        if col in filtered_df.columns:
            # First replace "-" with 0
            filtered_df[col] = filtered_df[col].replace("-", 0)
            
            # Identify "D" values
            d_mask = filtered_df[col] == "D"
            
            # Convert column to numeric, "D" will become NaN temporarily
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors="coerce")
            
            # For each region and group combination, replace NaN values from "D" with the mean
            if d_mask.any():
                print(f"Replacing {d_mask.sum()} 'D' values in {col} column with region-specific group means")
                
                # Get all combinations of Region, Group, and Subgroup where we have "D" values
                d_combinations = filtered_df[d_mask][['Region', 'Group', 'Subgroup']].drop_duplicates().values
                
                for region, group, subgroup in d_combinations:
                    # Calculate mean for this region and group (excluding NaN values)
                    group_mean = filtered_df[
                        (filtered_df['Region'] == region) & 
                        (filtered_df['Group'] == group) &
                        (filtered_df[col].notna())
                    ][col].mean()
                    
                    # If we don't have enough data for a specific mean, use a more general one
                    if pd.isna(group_mean) or group_mean == 0:
                        group_mean = filtered_df[
                            (filtered_df['Region'] == region) & 
                            (filtered_df[col].notna())
                        ][col].mean()
                    
                    # If still not enough data, use the overall mean for the column
                    if pd.isna(group_mean) or group_mean == 0:
                        group_mean = filtered_df[filtered_df[col].notna()][col].mean()
                    
                    # Replace NaN values for this specific combination
                    filtered_df.loc[
                        (filtered_df['Region'] == region) & 
                        (filtered_df['Group'] == group) & 
                        (filtered_df['Subgroup'] == subgroup) & 
                        (d_mask),
                        col
                    ] = group_mean
    
    # Drop the original 'Characteristic' column as we now have Group and Subgroup
    if "Characteristic" in filtered_df.columns:
        filtered_df.drop(columns=["Characteristic"], inplace=True)
    
    # Handle special case of "Total" region - this should be removed
    filtered_df = filtered_df[filtered_df["Region"] != "Total"]
    
    # Output the refined dataset
    filtered_df.to_excel(output_file_path, index=False)
    
    print(f"Processing complete. Filtered data saved to {output_file_path}")
    print(f"Dataset contains {len(filtered_df)} rows with data from Age, Occupation, and Broad Class of Admission categories.")
    print(f"Data spans {len(filtered_df['Year'].unique())} years and {len(filtered_df['Region'].unique())} regions.")