import sublime
import sublime_plugin
import webbrowser
import json
import urllib
from .lib import store, util, snippets

config = util.load_config()


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
        url = "{0}/sublime/validate".format(config["hosts"]["api"])

        try:
            req = urllib.request.Request(url, data=None, headers=headers, method="POST")
            urllib.request.urlopen(req)

            store.set_val("logged_in", True)
            util.save_credentials(setup_api_key_handler, setup_api_token_handler)
            snippets.initialize()

            sublime.status_message("Cacher: Logged in")
        except urllib.error.HTTPError as e:
            self.__handle_error(e)

    def input(self, args):
        webbrowser.open("{0}/enter?action=view_api_creds".format(config["hosts"]["app"]))
        return SetupApiKeyHandler(self.view)

    @staticmethod
    def __handle_error(e):
        resp = json.loads(e.read().decode("utf8"))

        if e.code == 403:
            if resp["error_code"] == "NoPermission":
                sublime.error_message("Cacher API key or token not valid. Please try again.")
            else:
                sublime.error_message("Upgrade to the Pro or Team plan to use Sublime with Cacher.")
        else:
            sublime.error_message("There was an error communicating with Cacher. Please try again.")
