from promp_toolkit_validators import Validators
from models import session, App
import time
from vault import CURRENT_USER
from tabulate import tabulate
from main import index
import utils
from utils import PromptStyle
import sqlalchemy as sa
from cryptography.fernet import Fernet
from prompt_toolkit import prompt
import pyperclip
from selenium import webdriver

def add_credential():
    print("\nAdd Credential\n")
    app_name = prompt("App Name: ", validator=Validators.is_not_empty()).lower().strip()
    app_url = prompt("App URL: ")
    app_username = prompt("Username: ", validator=Validators.is_not_empty())
    app_password = prompt("Password: ", is_password=True, validator=Validators.is_not_empty())

    fernet = Fernet(CURRENT_USER.key)
    app_password = fernet.encrypt(app_password.encode())

    app = App(name=app_name, user_id=CURRENT_USER.id, url=app_url, username=app_username, password=app_password)

    try:
        session.add(app)
        session.commit()
    except Exception as e:
        PromptStyle.danger(f"Error occured during adding credentials: {e}")

    text = f"\nAdded Credential Successfully.\n"

    PromptStyle.success(text)

    print("You will be redirected back to index...")
    time.sleep(5)
    index()


def show_credential():
    print("\nShow Credentials.\n")
    apps = CURRENT_USER.get_apps()
    if not apps['id']:
        create_choice = prompt("You have no credentials save. Would you like to add a new one? (Y/N): ").lower().strip()
        if create_choice == "y":
            return add_credential()
        elif create_choice == "n":
            return index()
        else:
            print("Invalid action. You will be redirected back to index page.")
            return index()

    print("The table below shows you all of your saved credentials.\n")
    print(tabulate(apps, tablefmt='grid', headers='keys'))
    print("\nWhat would you like to do next?\n")
    options = [
        '(1) View Password',
        '(2) Copy Password',
        '(3) Back'
    ]

    utils.options_transition(options)

    choice = int(prompt("\nPlease select an option: ", validator=Validators.is_number(), validate_while_typing=False))

    match choice:
        case 1:
            view_password()
        case 2:
            copy_password()
        case 3:
            index()


def delete_credential():
    print("\nDelete Credential\n")
    apps = CURRENT_USER.get_apps()
    if not apps['id']:
        delete_choice = prompt("There's no credentials to delete. Woul you like to add one first? (Y/N): ").lower().strip()
        if delete_choice == "y":
            print("\nAdd Credential\n")
            return add_credential()
        elif delete_choice == "n":
            return index()
        else:
            print("Invalid action. You will be redirected back at index page.")
            return index()

    print(tabulate(apps, tablefmt='grid', headers='keys'))
    app_to_delete = prompt("Please select the name from table above the credential you want to delete: ").lower().strip()
    while app_to_delete not in apps['name']:
        print(f"\nYou have no saved credentials at {app_to_delete}.\n")
        app_to_delete = prompt("Please select the name from table above the credential you want to delete: ").lower().strip()

    app_id = session.scalar(sa.select(App.id).where(App.name == app_to_delete))
    try:
        session.delete(session.get(App, int(app_id)))
        session.commit()
    except Exception as e:
        print(f"An error occured during deletion of your credentials: {e}")
    else:
        print("Your credential has been deleted.\n")
        print("You will be redirected back to index...")
        time.sleep(5)
        return index()


def view_password():
    print("\nView Password\n")
    apps = CURRENT_USER.get_apps()
    app_name = prompt("Please enter the application name to view your password: ", validator=Validators.is_not_empty()).strip().lower()

    while app_name not in apps['name']:
        create_credential = prompt(f"\nYou don't have a saved credentials at {app_name}. Would you like to create one? (Y/N): ").lower().strip()
        if create_credential == "y":
            return add_credential()
        app_name = prompt("\nPlease select an app to view your password: ", validator=Validators.is_not_empty()).lower().strip()

    app = session.scalar(sa.select(App).where(App.name == app_name))
    master_password = prompt("Password: ", validator=Validators.valid_password(), is_password=True, validate_while_typing=False)

    if master_password:
        fernet = Fernet(CURRENT_USER.key)
        password = fernet.decrypt(app.password)
        app_info = {'id': [app.id], 'url': [app.url], 'name': [app.name], 'password': [password.decode()]}
        print("\n" + tabulate(app_info, tablefmt='grid', headers='keys'))

    options = [
        '(1) Copy password',
        '(2) Go to URL',
        '(3) Back'
    ]

    print("\nWhat would you like to do next?\n")

    utils.options_transition(options)

    choice = int(prompt("\nPlease choose an action: ", validator=Validators.is_number()))

    match choice:
        case 1:
            try:
                pyperclip.copy(app_info['password'][0])
                print("\nPassword copied to clipboard. You only have 15 seconds to use this.\n")
                time.sleep(15)
                pyperclip.copy("")
            except pyperclip.PyperclipException:
                print(f"\nClipboard not available. Copy manually: {app_info['password'][0]}\n")
            finally:
                print("You have 10 seconds to copy your password. You will be redirected back to index in just a seconds...")
                time.sleep(10)
                return index()
        case 2:
             ...
        case 3:
            show_credential()


def copy_password():
    app_name = prompt("Enter the name of the app you want to copy your password: ", validator=Validators.is_not_empty(), validate_while_typing=False)
    app = session.scalar(
        sa.select(App.password).where(App.name == app_name)
    )
    while not app:
        create_credential = prompt(f"\nYou don't have a saved credentials at {app_name}. Would you like to create one? (Y/N): ").lower().strip()
        if create_credential == "y":
            return add_credential()
        return index()

    fernet = Fernet(CURRENT_USER.key)
    password = fernet.decrypt(app).decode()

    try:
        pyperclip.copy(password)
    except pyperclip.PyperclipException:
        print(f"\nClipboard not available. Copy manually: {password}\n")
    finally:
        print("You have 10 seconds to copy your password. You will be redirected back to index in just a seconds...")
        time.sleep(10)
        return index()


def go_to_url():
    print("\nOpening URL...\n")
    