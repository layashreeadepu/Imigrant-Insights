# main_script.py
import sys
import os
sys.path.append(os.path.abspath("C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Mergefn/immigration"))
from immigration.merger import load_and_clean_data

input_folder = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/"
final_df = load_and_clean_data(input_folder)

# Now you can use final_df as you like 
print(final_df.head())
final_df.to_excel("C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Merged files/cleaned_data.xlsx", index=False)

