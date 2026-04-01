import time
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text

class PromptStyle():
    """Aesthetically change text color of feedback based on user action."""

    @staticmethod
    def success(text: str) -> None:
        print_formatted_text(FormattedText([('ansigreen', text)]))

    @staticmethod
    def danger(text: str) -> None:
        print_formatted_text(FormattedText([('ansired', text)]))

    @staticmethod
    def warning(text: str) -> None:
        print_formatted_text(FormattedText([('ansiyellow', text)]))


def options_transition(list_options):
    for option in list_options:
        for c in option:
            print(c, end="", flush=True)
            time.sleep(0.05)
        print()
