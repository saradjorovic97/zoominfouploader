#MAIN SCRIPT: for now you have to run it manually every time you make changes to the Excel file
#Unlike the initial uploader it will only upload new ZoomInfo Contact IDs that haven't been uploaded before

import pandas as pd
import os
import requests
from datetime import datetime, timezone
#import socket  # if you want to use your PC name as the uploader
#import numpy as np (testing something later), pip install if needed

EXCEL_PATH = r'C:\Users\Korisnik\Documents\ZoomInfo CSV Drops.xlsx'  # change this if your file is somewhere else
DEPLOYMENT_URL = "https://script.google.com/macros/whatever"  # your Apps Script web app URL (deployment -> new -> set to "anyone with the link")
UPLOADER = "ManuallyInputtedUsername"  # or socket.gethostname() if you want the computer name

EXISTING_LEADS = r"C:\Users\Korisnik\Documents\existingleads.txt" # change this if your directory is different

#Whatever columns you need -- make sure these exact names exist in the Excel file
#and match what the Google Apps Script expects as well as the collumns in the initialuploader.py script
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

def loadexistingleads() -> set:
    if not os.path.exists(EXISTING_LEADS):
        return set()

    with open(EXISTING_LEADS, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())  
    
def saveexistingleads(leads: set):
    with open(EXISTING_LEADS, "w", encoding="utf-8") as f:
        for lead in sorted(leads):
            f.write(f"{lead}\n")

def uploader(): 
    log(f"Script started...")
    if not os.path.exists(EXCEL_PATH):
        log(f"ERROR: Excel file not found at {EXCEL_PATH}, exiting.")
        return
    else:
        log("Reading Excel file...")
    
    try:
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    except Exception as e:
        log(f"Failed to read Excel file: {e}")
        return

    log(f"Total leads in Excel: {len(df)}")

    missing = [c for c in EXCEL_COLUMNS if c not in df.columns]
    if missing:
        log(f"Missing columns: {missing}")
        return
    
    existingleads = loadexistingleads()
    log(f"Previously loaded leads: {len(existingleads)}")

    df = df[df["ZoomInfo Contact ID"].astype(str).notna()]
    df["ZoomInfo Contact ID"] = df["ZoomInfo Contact ID"].astype(str)

    newleads = df[~df["ZoomInfo Contact ID"].isin(existingleads)]

    log(f"New leads to upload: {len(newleads)}")
    if newleads.empty:
        log("No new leads to upload, exiting.")
        return

    newleads = newleads[EXCEL_COLUMNS]
    newleads.replace(to_replace=[pd.NA, float("nan"), float("inf"), float("-inf")], value="", inplace=True)
    #or maybe newleads = newleads.fillna("") if no risk of inf/-inf, just pip install numpy 

    #METADATA, don't edit
    newleads.insert(0, "uploaded_at", datetime.now(timezone.utc).isoformat())
    newleads.insert(0, "uploaded_by", UPLOADER)

    payload = {"rows": newleads.to_dict(orient="records")}
    log("Uploading new rows...")
    try:
        response = requests.post(DEPLOYMENT_URL, json=payload, timeout=60)
    except requests.RequestException as e:
        log(f"HTTP request failed: {e}")
        log("Upload failed, state NOT updated")
        return
    log(f"HTTP status: {response.status_code}")
    log(f"Response body: {response.text}")

    if response.status_code == 200 and response.text.strip().startswith("OK"):
        existingleads.update(newleads["ZoomInfo Contact ID"])
        saveexistingleads(existingleads)
        log("Upload successful, state updated")
    else:
        log("Upload failed, state NOT updated")

    log("FINISHED")


if __name__ == "__main__":
    uploader()