from prompt_toolkit.validation import Validator
from models import User, session
import sqlalchemy as sa
from werkzeug.security import check_password_hash

CURRENT_USER = None

class Validators:
    @classmethod
    def is_number(cls) -> Validator:
        return Validator.from_callable(
            lambda text: text.isdigit(),
            error_message = "Input contains non-numeric characters.",
            move_cursor_to_end = True
        )

    @classmethod
    def length_checker(cls) -> Validator:
        return Validator.from_callable(
            lambda text: 8 <= len(text) <= 20,
            error_message = "Input must be between 8 to 20 characters.",
            move_cursor_to_end = True
        )

    @staticmethod
    def is_valid(text: str) -> bool:
        user = session.scalar(
            sa.select(User).where(User.username == text)
        )
        return False if user is not None else True

    @classmethod
    def validate_username(cls):
        return Validator.from_callable(
            cls.is_valid,
            error_message = "Username already exist.",
            move_cursor_to_end = True
        )

    @staticmethod
    def is_registered(text: str):
        user = session.scalar(
            sa.select(User).where(User.username == text)
        )
        global CURRENT_USER
        CURRENT_USER = user
        return False if user is None else True

    @classmethod
    def valid_username(cls):
        return Validator.from_callable(
            cls.is_registered,
            error_message = "Incorrect Username.",
            move_cursor_to_end = True
        )

    @staticmethod
    def check_password(text: str) -> bool:
        user = session.scalar(
            sa.select(User.master_password).where(User.username == CURRENT_USER.username)
        )
        return check_password_hash(user, text)

    @classmethod
    def valid_password(cls):
        return Validator.from_callable(
            cls.check_password,
            error_message = "Incorrect Password.",
            move_cursor_to_end = True
        )

    @classmethod
    def is_not_empty(cls):
        return Validator.from_callable(
            lambda text: bool(text.strip()),
            error_message = "Input should not be empty.",
            move_cursor_to_end = True
        )
