import json
import os
#from typing import List

from dotenv import load_dotenv
from flask import current_app, abort
import gspread
from gspread.exceptions import SpreadsheetNotFound, APIError

load_dotenv()

DOCUMENT_ID = os.environ.get('GOOGLE_SHEET_ID')
CREDS = os.environ.get('GOOGLE_API_CREDENTIALS')
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

class Spreadsheet():
    def __init__(self):
        if CREDS:
            self.credentials = json.loads(CREDS)
        else:
            current_app.logger.error('GOOGLE_API_CREDENTIALS is undefined.')
            abort(500, 'GOOGLE_API_CREDENTIALS is undefined.')
        self.client = gspread.service_account_from_dict(self.credentials, scopes=SCOPES)
        self.sheet_id = DOCUMENT_ID
        self.sheet_name = None
        self.sheet = None
        self.range = None

    def get_sheet(self):
        try:
            doc = self.client.open_by_key(self.sheet_id) # <class 'gspread.models.Spreadsheet'>
            self.sheet = doc.worksheet(self.sheet_name) # <class 'gspread.models.Worksheet'>
        except APIError:
            current_app.logger.error(f"Sheet with id {self.sheet_id} was not found.")
            abort(404, f"gspread error: Sheet with id {self.sheet_id} was not found.")

    def get_records(self):
        self.get_sheet()
        self.records = self.sheet.get_all_records()
        return self.records

    def append_record(self, values):
        self.get_sheet()
        response = self.sheet.append_row(values, value_input_option="USER_ENTERED", table_range=self.range)
        return response

    def remove_record(self):
        pass

    def update_record(self):
        pass