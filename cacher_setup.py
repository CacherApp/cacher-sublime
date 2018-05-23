import sublime
import sublime_plugin
import webbrowser
import json
import urllib
import yaml
import os

file_dir = os.path.dirname(__file__)
with open(os.path.join(file_dir, "config.yml"), "r") as ymlfile:
    config = yaml.load(ymlfile)


def validate_input(expr):
    return len(expr) > 0


class SetupApiTokenHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view):
        self.view = view

    @staticmethod
    def placeholder():
        return "API Token"

    @staticmethod
    def validate(expr):
        return validate_input(expr)

    def confirm(self, text):
        return [self.view.api_key, text]


class SetupApiKeyHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view):
        self.view = view
        webbrowser.open("{0}/enter?action=view_api_creds".format(config["hosts"]["app"]))

    @staticmethod
    def placeholder():
        return "API Key"

    @staticmethod
    def validate(expr):
        return validate_input(expr)

    def confirm(self, text):
        self.view.api_key = text
        return text

    def next_input(self, args):
        return SetupApiTokenHandler(self.view)


class CacherSetupCommand(sublime_plugin.TextCommand):
    def run(self, edit, setup_api_key_handler, setup_api_token_handler):
        headers = {
            'X-Api-Key': setup_api_key_handler,
            'x-Api-Token': setup_api_token_handler
        }
        url = "{0}/vscode/validate".format(config["hosts"]["api"])

        try:
            req = urllib.request.Request(url, data=None, headers=headers, method="POST")
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            self._handle_error(e)

        # sublime.status_message("Cacher: Token is valid!")

    def input(self, args):
        return SetupApiKeyHandler(self.view)

    @staticmethod
    def _handle_error(e):
        resp = json.loads(e.read().decode("utf8"))

        if e.code == 403:
            if resp["error_code"] == "NoPermission":
                sublime.error_message("Cacher API key or token not valid. Please try again.")
            else:
                sublime.error_message("Upgrade to the Pro or Team plan to use Sublime with Cacher.")
        else:
            sublime.error_message("There was an error communicating with Cacher. Please try again.")
