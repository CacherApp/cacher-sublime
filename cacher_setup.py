import sublime
import sublime_plugin
import webbrowser
import json
import urllib
import time
from .lib import util, snippets

global last_run
last_run = -1


class SetupApiTokenHandler(sublime_plugin.TextInputHandler):
    @staticmethod
    def placeholder():
        return "API Token"

    @staticmethod
    def validate(expr):
        return util.validate_input(expr)

    @staticmethod
    def confirm(text):
        return text


class SetupApiKeyHandler(sublime_plugin.TextInputHandler):
    @staticmethod
    def placeholder():
        return "API Key"

    @staticmethod
    def validate(expr):
        return util.validate_input(expr)

    @staticmethod
    def confirm(text):
        return text

    @staticmethod
    def next_input(args):
        return SetupApiTokenHandler()


class CacherSetupCommand(sublime_plugin.TextCommand):
    def run(self, edit, setup_api_key_handler, setup_api_token_handler):
        headers = {
            'X-Api-Key': setup_api_key_handler,
            'x-Api-Token': setup_api_token_handler
        }
        url = "{0}/sublime/validate".format(util.settings().get("apiHost"))

        try:
            req = urllib.request.Request(url, data=None, headers=headers, method="POST")
            urllib.request.urlopen(req)

            util.store().set("logged_in", True)
            util.save_credentials(setup_api_key_handler, setup_api_token_handler)
            snippets.load_snippets()

            sublime.status_message("Cacher: Logged in")
        except urllib.error.HTTPError as e:
            self.__handle_error(e)

    @staticmethod
    def input(args):
        # De-dupe multiple calls
        global last_run
        if int(time.time()) - last_run < 5:
            return SetupApiKeyHandler()
        last_run = int(time.time())

        if sublime.ok_cancel_dialog("Open Cacher to view credentials", "Open Cacher"):
            webbrowser.open("{0}/enter?action=view_api_creds".format(util.settings().get("appHost")))
        return SetupApiKeyHandler()

    @staticmethod
    def __handle_error(e):
        resp = json.loads(e.read().decode("utf8"))

        if e.code == 403:
            if resp["error_code"] == "NoPermission":
                sublime.error_message("Cacher API key or token not valid. Please try again.")
            else:
                if sublime.ok_cancel_dialog("Upgrade to the Pro or Team plan to use Sublime with Cacher.", "View Plans"):
                    webbrowser.open("{0}/enter?action=view_plans".format(util.settings().get("appHost")))
        else:
            sublime.error_message("There was an error communicating with Cacher. Please try again.")
