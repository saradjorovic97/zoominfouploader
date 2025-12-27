# ZoomInfo CSV files to Google Sheets Uploader

Simple Python scripts to upload ZoomInfo Sales OS leads (exported as CSV) to a shared Google Sheets spreadsheet.  
Built for internal use at companies without direct ZoomInfo → CRM integration. Tracks who uploaded what and when. The scripts are heavily commented/logged because this is an internal tool for my coworkers to use and debugging matters since it needs some tweaking.

There are **two scripts**:
- initialuploader.py → Run **ONLY ONCE** (uploads the intial batch, no deduping).
- mainuploader.py → Run manually whenever new data is ready (only uploads new ZoomInfo Contact IDs).

## Requirements & Setup

### 1. Python & Dependencies
- Python 3.x
- Install required packages: pip -m install pandas requests openpyxl
### 2. Excel File (via Power Query)
- Set up an Excel sheet that auto-appends new ZoomInfo CSV files (Power Query is super easy to set up and works great for me so far, will see at the number of leads grows — refresh every 1/3/5/10 minutes).
- Note: ZoomInfo downloads CSVs to your browser's default folder and at least for me there's no way to change this. If it downloads to the default folder it clashes with other downloads and causes errors. Use a dedicated browser/profile that downloads to a specific folder to avoid clashes -- plus it's easier to backup your CSVs that way.

### 3. Google Sheets + Apps Script
- Create a Google Sheet, set access to public (or "anyone with link").
- Deploy an Apps Script as a Web App:
- Execute as: Me
- Access: Anyone (or Anyone with the link)
- Set SHEET_NAME = "Main" in the Apps Script (or change it there).
- Copy the deployment URL → paste into DEPLOYMENT_URL in both Python scripts.
- Set your Spreadsheet ID in the Apps Script.

### 4. Configure the Scripts
In both "initialuploader.py" and "mainuploader.py":
- Update EXCEL_PATH to your consolidated Excel file.
- Update DEPLOYMENT_URL.
- Set UPLOADER to your or your coworkers' name (or uncomment socket.gethostname() -- but in our setup that pulls the IT admin's name).

## Usage

1. Run the initial uploader **once** (processes everything):
python initialuploader.py
2. After that, run the main uploader whenever the Excel updates:
python mainuploader.py
**WARNING**: Do NOT run initialuploader more than once — it'll create duplicates.

## Dependencies
- Python libraries: pandas, requests, openpyxl
- Google Apps Script (deployed as web app)

If something breaks, check the console logs -- they're verbose on purpose.
