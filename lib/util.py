import sublime
import os.path
import json
from urllib.parse import urlparse, urlencode
import webbrowser

home = os.path.expanduser("~")
cacher_dir = os.path.join(home, ".cacher")
credentials_file = os.path.join(cacher_dir, "credentials.json")


def credentials_exist():
    return os.path.exists(credentials_file)


def get_credentials():
    with open(credentials_file, "r") as creds_file:
        return json.load(creds_file)


def save_credentials(key, token):
    if not os.path.exists(cacher_dir):
        os.mkdir(cacher_dir)

    with open(credentials_file, "w") as file:
        content = {"key": key, "token": token}
        json.dump(content, file)


def settings():
    return sublime.load_settings("Cacher.sublime-settings")


def store():
    return sublime.load_settings("Cacher Store.sublime-settings")


def validate_input(expr):
    return len(expr) > 0


def request_headers():
    credentials = get_credentials()
    return {
        'X-Api-Key': credentials["key"],
        'X-Api-Token': credentials["token"]
    }


def prompt_user_setup():
    if sublime.ok_cancel_dialog("Cacher needs to be setup before use", "Start Setup"):
        sublime.active_window().run_command("cacher_setup")


def open_url(url):
    result = urlparse(url)

    # Validate URL before opening
    if result.scheme and result.netloc and result.path:
        webbrowser.open(url)


def open_app_url(path, **kwargs):
    url = settings().get("appHost") + path + "?" + urlencode(kwargs)
    open_url(url)


def show_server_error():
    sublime.error_message("There was an error communicating with the Cacher server. Please try again.")


def show_credentials_parse_error():
    sublime.error_message(
        "There was an error loading your Cacher credentials file. Please run \"Cacher: Setup\"."
    )
