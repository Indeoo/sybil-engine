import csv
import datetime
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from loguru import logger

from sybil_engine.utils.telegram import get_config

statistic_date_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class StatisticsWriter:
    def init_if_required(self, job_name, header):
        pass

    def write_row(self, job_name, row):
        pass


class CsvStatisticsWriter(StatisticsWriter):
    def init_if_required(self, job_name, header):
        output_file = self._get_file_name(job_name)
        file_exists = os.path.isfile(output_file)

        rows_to_write = []

        if not file_exists or os.path.getsize(output_file) == 0:
            rows_to_write.append(header)

        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows_to_write)

    def write_row(self, job_name, row):
        rows_to_write = []
        output_file = self._get_file_name(job_name)

        rows_to_write.append(row)

        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows_to_write)

    def _get_file_name(self, job_name):
        return f'data/csv/{job_name}.csv'


class GoogleStatisticsWriter(StatisticsWriter):
    SERVICE_ACCOUNT_FILE = 'data/service-accounts.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    def __init__(self, sheet):
        self.sheet = sheet

    def init_if_required(self, sheet_name, header):
        if not self._sheet_exists(sheet_name):
            self._create_new_sheet(sheet_name)
            self.write_row(sheet_name, header)

    def _sheet_exists(self, sheet_name):
        try:
            self.service.spreadsheets().values().get(spreadsheetId=self.sheet, range=sheet_name).execute()
            logger.info('Sheet exists.')
            return True
        except Exception:
            return False

    def _create_new_sheet(self, sheet_name):
        body = {'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]}
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.sheet, body=body).execute()
        logger.info(f'Sheet "{sheet_name}" created.')

    def write_row(self, job_name, row):
        range_ = f"{job_name}!A1"
        rows_read = self.service.spreadsheets().values().get(spreadsheetId=self.sheet, range=range_).execute().get(
            'values', [])
        body = {'values': [row]}
        range_to_write = f"{job_name}!A{len(rows_read) + 1}"
        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet, range=range_to_write, valueInputOption='USER_ENTERED', body=body
        ).execute()
        logger.info(f'Row written: {row}')


def get_statistic_writer():
    if get_config("STATISTICS_MODE") == "CSV":
        return CsvStatisticsWriter()
    else:
        return GoogleStatisticsWriter(get_config("SPREADSHEET_ID"))
