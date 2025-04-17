from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import requests

# Function to generate a unique filename
def get_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    return unique_name

# Setup Chrome driver (headless optional)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # comment out to see browser

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to main site
url = "https://ohss.dhs.gov/topics/immigration/lawful-permanent-residents/profiles"
driver.get(url)
time.sleep(5)

# Path to save files
sv_path = 'C:/Users/layas/OneDrive/Desktop/Layashree documents/NEU Cources/Intro to Programming in DS/input dataset/all cont'

# Show all entries in dropdown (to get all rows)
try:
    show_all = driver.find_element(By.NAME, "table_cob_length")  # this is the dropdown for # of rows shown
    for option in show_all.find_elements(By.TAG_NAME, "option"):
        if "All" in option.text:
            option.click()
            break
    time.sleep(3)  # wait for table to reload
except:
    print("Could not select 'All' option.")

# Filter only "Profiles by Country of Birth" section table
table = driver.find_element(By.ID, "table_cob")
rows = table.find_elements(By.TAG_NAME, "tr")

# Extract download links for ZIP, XLS, XLSX files
download_links = []
for row in rows:
    try:
        link_elem = row.find_element(By.TAG_NAME, "a")
        file_link = link_elem.get_attribute("href")
        if file_link and (
            file_link.endswith(".zip") or
            file_link.endswith(".xls") or
            file_link.endswith(".xlsx")
        ):
            download_links.append(file_link)
    except:
        continue  # not all rows have links

print(f"Found {len(download_links)} file links.")

# Save links
with open("country_birth_links.txt", "w") as f:
    for link in download_links:
        f.write(link + "\n")

# Make download folder
os.makedirs(sv_path, exist_ok=True)

# Download files
for link in download_links:
    original_filename = link.split("/")[-1]
    unique_filename = get_unique_filename(sv_path, original_filename)
    full_path = os.path.join(sv_path, unique_filename)
    print(f"Downloading {unique_filename}")

    try:
        r = requests.get(link)
        r.raise_for_status()
        with open(full_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        print(f"Error downloading {original_filename}: {e}")

driver.quit()
print("All downloads done!")
