import json
import os
#from typing import List

from dotenv import load_dotenv
from flask import abort
import gspread
from gspread.exceptions import APIError

load_dotenv()

DOCUMENT_ID = os.environ.get('GOOGLE_SHEET_ID')
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

class Spreadsheet():
    """A class for a Google Spreasheet object"""
    def __init__(self, app):
        self.current_app = app
        if os.path.exists('./creds.json'):
            with open('./creds.json', mode='r', encoding='utf-8') as fp:
                json.load(fp)
        elif (creds := os.environ.get('GOOGLE_API_CREDENTIALS', None)):
            self.credentials = json.loads(creds)
        else:
            self.current_app.logger.error('GOOGLE_API_CREDENTIALS is undefined.')
            abort(500, 'GOOGLE_API_CREDENTIALS is undefined.')
            raise RuntimeError('GOOGLE_API_CREDENTIALS is undefined.')
        self.client = gspread.service_account_from_dict(self.credentials, scopes=SCOPES)
        self.sheet_id = DOCUMENT_ID
        self.records = None
        self.sheet_name = None
        self.sheet = None
        self.range = None

    def get_sheet(self):
        """Get a sheet by name or ID"""
        try:
            doc = self.client.open_by_key(self.sheet_id) # <class 'gspread.models.Spreadsheet'>
            self.sheet = doc.worksheet(self.sheet_name) # <class 'gspread.models.Worksheet'>
        except APIError:
            self.current_app.logger.error(f"Sheet with id {self.sheet_id} was not found.")
            abort(404, f"gspread error: Sheet with id {self.sheet_id} was not found.")

    def get_records(self):
        """Get all the records of the spreadsheet"""
        self.get_sheet()
        self.records = self.sheet.get_all_records()
        return self.records

    def append_record(self, values):
        """Append a record to the spreadsheet"""
        self.get_sheet()
        response = self.sheet.append_row(values, value_input_option="USER_ENTERED", table_range=self.range)
        return response

    def remove_record(self):
        """Remove a record from the spreadsheet"""
        pass

    def update_record(self):
        """Edit a record of the spreadsheet"""
        pass