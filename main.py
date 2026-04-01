from pyfiglet import Figlet
from promp_toolkit_validators import Validators
from prompt_toolkit import prompt
import utils
import sys

def index():
    from vault import CURRENT_USER, logout
    from credentials import add_credential, show_credential, delete_credential
    print(f"\nWelcome {CURRENT_USER.username}\n")
    options = [
        '(1) Add credential',
        '(2) View credentials',
        '(3) Delete credential',
        '(4) Logout'
    ]

    utils.options_transition(options)

    print()

    choice = int(prompt("Please choose an action: ", validator=Validators.is_number()))

    match choice:
        case 1:
            add_credential()
        case 2:
            show_credential()
        case 3:
            delete_credential()
        case 4:
            logout()


def show_menu():
    from vault import login, create_account
    f = Figlet(font='rectangles')
    print(f.renderText('welcome'))
    print('Please select an option.\n')
    options = [
        '(1) Create an account',
        '(2) Login',
        '(3) Reset Your Password',
        '(4) About',
        '(5) Exit'
    ]

    utils.options_transition(options)

    print()

    choice = int(prompt("Please select an option: ", validator=Validators.is_number()))

    match choice:
        case 1:
            create_account()
        case 2:
            login()
        case 3:
            print("\nTo be implemented soon...\n")
        case 4:
            print("""

ABOUT

Password Manager is a secure and intuitive command-line application designed to protect and organize your credentials. Built with strong encryption and authentication mechanisms, it allows users to safely register, log in, and manage sensitive information such as usernames and passwords for different services.

Features include:

    • Encrypted storage using Fernet for safeguarding application passwords.

    • Authentication system with hashed master passwords via werkzeug.security.

    • Credential management, including adding, viewing, and deleting saved entries.

    • User-friendly CLI interface that makes navigating features seamless and efficient.

Whether you're a developer managing multiple accounts or just someone looking for a lightweight password tool, this program offers a reliable solution tailored for terminal environments.
            """)
            show_menu()
        case 5:
            sys.exit("\nGoodbye motherfucker\n")
