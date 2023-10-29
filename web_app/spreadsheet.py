import pathlib as pl
from dataclasses import dataclass, field
from typing import Any, Dict, List, NoReturn

import gspread as gs
from gspread.exceptions import APIError, WorksheetNotFound


class SpreadsheetError(Exception):
    """A subclass for exceptions raised by the Spreadsheet class"""


@dataclass
class Spreadsheet:
    """A class for a Google Spreasheet object"""

    credentials: pl.Path
    _client: gs.Client | None = field(init=False, default=None)
    _spreadsheet_id: str | None = None  # the spreadsheet ID
    _sheet_name: str | None = None  # the sheet name
    _doc: gs.Spreadsheet | None = None
    _sheet: gs.Worksheet | None = None
    _range: str | None = None  # the table range

    def __post_init__(self) -> None:
        """Initialize the class"""
        if not self.credentials.exists():
            raise SpreadsheetError(
                f"Credentials file '{self.credentials}' does not exist."
            )

        self._client = gs.service_account(filename=self.credentials)

    # Properties with accessors
    @property
    def client(self) -> gs.Client:
        """Returns the client object"""
        if not self._client:
            raise SpreadsheetError(
                "Spreadsheet client is uninitialized. Did you pass valid credentials?"
            )
        return self._client

    @client.setter
    def client(self, _) -> NoReturn:
        raise SpreadsheetError("Cannot set the client object.")

    @property
    def spreadsheet_id(self) -> str:
        """Returns the spreadsheet ID"""
        return self._spreadsheet_id or ""

    @spreadsheet_id.setter
    def spreadsheet_id(self, id_: str) -> None:
        self._spreadsheet_id = id_

    @property
    def sheet_name(self) -> str:
        """Returns the sheet (a.k.a. worksheet) name"""
        return self._sheet_name or ""

    @sheet_name.setter
    def sheet_name(self, name: str) -> None:
        self._sheet_name = name

    @property
    def doc(self) -> gs.Spreadsheet:
        """Returns the spreadsheet document object"""
        if not self.spreadsheet_id:
            raise SpreadsheetError("Spreadsheet ID is undefined.")

        try:
            doc = self.client.open_by_key(self.spreadsheet_id)
        except APIError:
            raise SpreadsheetError(
                "A spreadsheet with ID '{}' was not found.".format(self.spreadsheet_id)
            )

        self._doc = doc

        return self._doc

    @doc.setter
    def doc(self, _) -> NoReturn:
        raise SpreadsheetError(
            "Spreadsheet document should only be set by providing the spreadsheet ID."
        )

    @property
    def sheet(self) -> gs.Worksheet:
        """Returns a single sheet (a worksheet)"""
        try:
            sheet = self.doc.worksheet(self.sheet_name)
        except WorksheetNotFound:
            sheet = self.add_worsheet(self.sheet_name)

        self._sheet = sheet

        return self._sheet

    @sheet.setter
    def sheet(self) -> NoReturn:
        raise SpreadsheetError("Cannot set the sheet object.")

    @property
    def range(self) -> str:
        return self._range or ""

    @range.setter
    def range(self, range: str) -> None:
        self._range = range

    # Methods
    def add_worsheet(self, title: str) -> gs.Worksheet:
        """Add a new worksheet to the spreadsheet"""
        if not title:
            raise SpreadsheetError("Worksheet title cannot be empty.")

        self.sheet_name = title

        return self.doc.add_worksheet(title, 100, 20)

    def create_spreasheet(self, title: str) -> str:
        """Create a new spreadsheet"""
        if self.spreadsheet_id:
            raise SpreadsheetError(
                "A spreadsheet with ID '{}' already exists.".format(self.spreadsheet_id)
            )

        doc = self.client.create(title)
        self.spreadsheet_id = doc.id
        self.add_worsheet("Expense Log")

        return self.spreadsheet_id

    def share_spreasheet(self, email: str, role: str = "writer") -> None:
        """Share the spreadsheet with a user"""
        self.doc.share(
            email,
            perm_type="user",
            role=role,
            notify=True,
            email_message="Google Sheets Flask created a new spreadsheet for you: "
            f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}",
        )

    def append_records(self, values: List[List[Any]]) -> Any:
        """Append one or more records to the spreadhseet"""
        return self.sheet.append_rows(
            values, value_input_option="USER_ENTERED", table_range=self.range
        )

    def get_records(
        self,
        sheet_name: str | None = None,
        range_: str | None = None,
        as_dict: bool = False,
        **kwargs,
    ) -> List | List[Dict]:
        """Get records from a range (A1 notation) or an entire sheet"""
        # If `sheet` is not given, check if it's already been set
        if sheet_name:
            self.sheet_name = sheet_name

        if self.sheet_name is None:
            all_sheets_names = [str(sheet.title) for sheet in self.doc.worksheets()]
            raise SpreadsheetError(
                "Cannot get data from an unnamed sheet! "
                f"Available sheets: '{', '.join(all_sheets_names)}'"
            )

        # Set the range if given
        if range_:
            self.range = range_

        if self.range:
            values = self.sheet.get_values(self.range)
        else:
            values = (
                self.sheet.get_all_records(**kwargs)
                if as_dict
                else self.sheet.get_all_values()
            )

        return values
