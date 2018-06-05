import sublime
import sublime_plugin
import json
import urllib
from .lib import util, snippets


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


class CacherSetupCommand(sublime_plugin.ApplicationCommand):
    def run(self, setup_api_key_handler, setup_api_token_handler):
        headers = {
            'X-Api-Key': setup_api_key_handler,
            'X-Api-Token': setup_api_token_handler
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
            self.handle_error(e)

    @staticmethod
    def input(args):
        if sublime.ok_cancel_dialog("Open Cacher to view credentials", "Open Cacher"):
            util.open_url(
                host=util.settings().get("appHost"),
                path="/enter",
                action="view_api_creds"
            )
        return SetupApiKeyHandler()

    @staticmethod
    def handle_error(e):
        try:
            resp = json.loads(e.read().decode("utf8"))
        except ValueError:
            util.show_server_error()

        if e.code == 403:
            if resp["error_code"] == "NoPermission":
                sublime.error_message("Cacher API key or token not valid. Please try again.")
            else:
                if sublime.ok_cancel_dialog("Upgrade to the Pro or Team plan to use Sublime with Cacher.", "View Plans"):
                    util.open_url(
                        host=util.settings().get("appHost"),
                        path="/enter",
                        action="view_plans"
                    )
        else:
            sublime.error_message("There was an error communicating with Cacher. Please try again.")
