# main_script.py
import sys
import os
#Merger function file path
sys.path.append(os.path.abspath("C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Mergefn/immigration"))
from immigration.merger import load_and_clean_data

#File path of xls file for datafile from year 2003 - 2023
input_folder = "C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/"
final_df = load_and_clean_data(input_folder)

#Print and export merged file
print(final_df.head())
final_df.to_excel("C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/Merged files/cleaned_data.xlsx", index=False)