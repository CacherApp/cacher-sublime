import sublime
import json
import urllib
from . import store, util

config = util.load_config()
global initialized
initialized = False


def initialize():
    if not initialized:
        load_snippets()


def load_snippets():
    if not util.credentials_exist():
        return

    url = "{0}/sublime/snippets".format(config["hosts"]["api"])

    try:
        req = urllib.request.Request(url, data=None, headers=__headers())
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode("utf8"))

        __set_store(data)
        global initialized
        initialized = True

        sublime.status_message("Cacher: Snippets loaded")
    except urllib.error.HTTPError as e:
        return


def __headers():
    credentials = util.get_credentials()
    return {
        'X-Api-Key': credentials["key"],
        'x-Api-Token': credentials["token"]
    }


def __set_store(data):
    __set_snippets(data)
    __set_teams(data)


def __set_snippets(data):
    store.set_val("personal_library", data["personalLibrary"])

    labels = data["personalLibrary"]["labels"]
    personal_snippets = []

    for snippet in data["personalLibrary"]["snippets"]:
        copy = dict()
        copy.update(snippet)

        copy["team"] = None
        copy["labels"] = __snippet_labels(labels, snippet)
        personal_snippets.append(copy)

    team_snippets = []

    for team in data["teams"]:
        labels = team["library"]["labels"]

        for snippet in team["library"]["snippets"]:
            copy = dict()
            copy.update(snippet)

            copy["team"] = team
            copy["labels"] = __snippet_labels(labels, snippet)
            team_snippets.append(copy)

    store.set_val("snippets", personal_snippets + team_snippets)


def __snippet_labels(labels, snippet):
    snippet_labels = []

    for label in labels:
        has_snippet = False
        for label_snippet in label["snippets"]:
            if label_snippet["guid"] == snippet["guid"]:
                has_snippet = True
        if has_snippet:
            snippet_labels.append(label["title"])

    return snippet_labels


def __set_teams(data):
    store.set_val("teams", data["teams"])
