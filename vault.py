from pynput.keyboard import Key, Listener
from prompt_toolkit import prompt
from promp_toolkit_validators import Validators
from models import User, session, init_db
from main import show_menu, index
import time
import sqlalchemy as sa
from utils import PromptStyle

CURRENT_USER = None

def main():
    init_db()
    show_menu()

def create_account():
    print("\nCreate an account.\n")
    username = prompt("Enter username: ", validator=Validators.validate_username())
    password = prompt("Enter password: ", is_password=True, validator=Validators.length_checker())

    user = User(username=username)
    user.set_password(password)
    user.set_salt()
    session.add(user)
    session.commit()
    PromptStyle.success("\nRegistered!\n")
    print("You will be redirected back at the menu prompt in just a moment.")
    print("Press ENTER if you don't want to wait.")

    time.sleep(5)

    show_menu()


def login():
    print("\nLogin to your account\n")
    username = prompt("Username: ", validator=Validators.valid_username(), validate_while_typing=False)
    password = prompt("Password: ", validator= Validators.valid_password(), validate_while_typing=False, is_password=True)

    try:
        user = session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            PromptStyle.warning("Invalid credentials")
            return show_menu()

        global CURRENT_USER
        CURRENT_USER = user
        CURRENT_USER.key = CURRENT_USER.generate_key(password)
        return index()

    except Exception as e:
        PromptStyle.danger(f"There was an error occured during logging in: {e}")


def logout():
    print("\nLogging out...\n")
    global CURRENT_USER
    CURRENT_USER = None
    session.rollback()
    return show_menu()


if __name__ == "__main__":
    main()
