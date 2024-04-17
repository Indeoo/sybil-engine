from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io
import csv

from loguru import logger


def get_google_spreadsheet(spreadsheet_id, sheet_name):
    # Define the scope
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    # Path to your service account key file
    SERVICE_ACCOUNT_FILE = 'data/service-accounts.json'
    # Spreadsheet details
    # Authenticate and construct service
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API to fetch data
    sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()

    logger.info(f"Loaded {sheet_name} from {spreadsheet_id}")

    data = sheet.get('values', [])

    csv_file_like = io.StringIO()
    csv_file_like.write('\n'.join([','.join(map(str, row)) for row in data]))
    csv_file_like.seek(0)
    # Now, use csv.DictReader to read this "file"
    reader = csv.DictReader(csv_file_like)

    rows = []
    for row in reader:
        rows.append(row)

    csv_file_like.close()

    return rows
