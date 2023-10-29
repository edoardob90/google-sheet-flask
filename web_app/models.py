import typing as t
import uuid
from dataclasses import dataclass, field


@dataclass
class User:
    """A class for a user"""

    _user_name: str = field(compare=False)
    _user_email: str | None = field(default=None, compare=False)
    _user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    _spreadsheet_id: str | None = field(default=None)

    @property
    def user_id(self) -> str:
        """Returns the unique user ID"""
        return self._user_id

    @user_id.setter
    def user_id(self, _: str) -> t.NoReturn:
        raise AttributeError("Cannot set user_id directly.")

    @property
    def user_name(self) -> str:
        """Returns the user name"""
        return self._user_name

    @user_name.setter
    def user_name(self, user_name: str) -> None:
        self._user_name = user_name

    @property
    def user_email(self) -> str | None:
        """Returns the user email"""
        return self._user_email

    @user_email.setter
    def user_email(self, user_email: str) -> None:
        self._user_email = user_email

    @property
    def spreadsheet_id(self) -> str | None:
        """Returns the spreadsheet ID"""
        return self._spreadsheet_id

    @spreadsheet_id.setter
    def spreadsheet_id(self, _: str) -> t.NoReturn:
        raise AttributeError("Cannot set spreadsheet_id directly.")


@dataclass
class Users:
    """A class for a collection of users"""

    users: t.Dict[str, User] = field(default_factory=dict)

    def add_user(self, user_name: str, user_email: str | None = None) -> User:
        new_user = User(user_name, user_email)
        self.users[new_user.user_id] = new_user
        return new_user

    def delete_user(self, user_id: str) -> None:
        self.users.pop(user_id, None)

    def get_user(self, user_id: str) -> User | None:
        return self.users.get(user_id, None)

    def get_user_by_name(self, user_name: str) -> User | None:
        for user in self.users.values():
            if user.user_name == user_name:
                return user
        return None

    def get_user_spreadsheet(self, user_id: str) -> str | None:
        user = self.get_user(user_id)
        return user.spreadsheet_id if user else None

    def set_user_spreadsheet(self, user_id: str, spreadsheet_id: str) -> None:
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID is invalid.")

        if user := self.get_user(user_id):
            user.spreadsheet_id = spreadsheet_id
        else:
            raise ValueError("User ID '{}' does not exist.".format(user_id))
