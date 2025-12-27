#Initial uploader script - RUN THIS ONLY ONCE!
#If you run it again, it'll flag all the same ZoomInfo Contact IDs as duplicates (the sheet side checks for that in the App Script)
#No memory here - it just grabs whatever is in the file and sends it

import pandas as pd
import os
import requests
from datetime import datetime, timezone
import socket  # if you want to use your PC name as the uploader
#import numpy as np (testing something later)

#python -m pip install pandas, openpyxl and whatever else you need if you haven't yet 

EXCEL_PATH = r'C:\Users\Korisnik\Documents\ZoomInfo CSV Drops.xlsx'  # change this if your file is somewhere else
DEPLOYMENT_URL = "https://script.google.com/macros/whatever"  # your Apps Script web app URL (deployment -> new -> set to "anyone with the link")
UPLOADER = "ManuallyInputtedUsername"  # or socket.gethostname() if you want the computer name

#Whatever columns you need -- make sure these exact names exist in the Excel file
#and match what the Google Apps Script expects
EXCEL_COLUMNS = [
    "ZoomInfo Contact ID",
    "First Name",
    "Last Name",
    "Email Address",
    "Direct Phone Number",
    "Mobile phone",
    "Company Name",
    "Website",
    "Company HQ Phone",
    "Company Country",
    #"Job Title",
]

def log(msg):
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def initialuploader():
    log("Starting the initial upload -- only run this once!!! Unless it fails :))")
    log(f"Looking for the Excel file here: {EXCEL_PATH}")

    if not os.path.exists(EXCEL_PATH):
        log("File not found, double-check the path.")
        return

    log("File found, loading it...")
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
        log("Excel loaded successfully.")
    except Exception as e:
        log(f"Couldn't read the file: {e}")
        return

    log(f"Got {len(df)} rows")
    log(f"Columns in the file: {list(df.columns)}")

    #Check for missing columns
    missing = set(EXCEL_COLUMNS) - set(df.columns)
    if missing:
        log(f"Missing columns that we need: {missing}")
        log("Fix the column names in the Excel or update EXCEL_COLUMNS list above.")
        return
    else:
        log("All required columns are there - good to go.")

    #Keep only the columns you want (order doesn't matter this way)
    df = df[EXCEL_COLUMNS]

    #Clean up any weird NaN/infinite values - replace with blank strings, don't edit
    df = df.replace([pd.NA, float('nan'), float('inf'), float('-inf')], "")
    #or maybe df = df.fillna(""), whichever works better 

    #Add metadata, don't edit 
    upload_time = datetime.now(timezone.utc).isoformat()
    df.insert(0, "Upload Time", upload_time)
    df.insert(0, "Lead Owner", UPLOADER)
    log("Added upload time and lead owner columns.")

    #Convert to the format the Apps Script expects, don't edit 
    payload = {"rows": df.to_dict(orient="records")}
    log(f"Prepared payload with {len(payload['rows'])} records.")

    log(f"Sending everything to Google Sheets via {DEPLOYMENT_URL}")
    try:
        resp = requests.post(DEPLOYMENT_URL, json=payload, timeout=60)
    except Exception as e:
        log(f"Request failed: {e}")
        return

    if resp.status_code == 200:
        log("Upload successful!")
        log(f"Response: {resp.text.strip()}")
    else:
        log(f"Upload failed - status code {resp.status_code}")
        log(f"Response body: {resp.text}")


if __name__ == "__main__":
    initialuploader()
    log("Script finished.")