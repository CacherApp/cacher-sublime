import sublime_plugin
from .lib import snippets


class CacherRefresh(sublime_plugin.ApplicationCommand):
    @staticmethod
    def run():
        snippets.load_snippets()
