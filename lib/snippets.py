import sublime
import json
import urllib
from . import util

global initialized
initialized = False


def initialize():
    if not initialized:
        load_snippets()


def snippet_with_guid(guid):
    for snippet in util.store().get("snippets"):
        if snippet["guid"] == guid:
            return snippet

    return None


def snippets_for_list():
    return list(map(list_snippet, util.store().get("snippets")))


def list_snippet(snippet):
    description = snippet.get("description", "")

    if snippet["team"]:
        description = "[{0}] {1}".format(snippet["team"]["name"], description)

    if len(snippet["labels"]) > 0:
        for label in snippet["labels"]:
            description = "({0}) {1}".format(label, description)

    title = "{0} - {1}".format(snippet["title"], description)
    title = title[:150]

    return title, snippet["guid"]


def load_snippets():
    if not util.credentials_exist():
        return

    url = "{0}/sublime/snippets".format(util.settings().get("apiHost"))

    try:
        req = urllib.request.Request(url, data=None, headers=util.request_headers())
        resp = urllib.request.urlopen(req)
        try:
            data = json.loads(resp.read().decode("utf8"))
        except ValueError:
            util.show_server_error()

        set_store(data)
        global initialized
        initialized = True

        sublime.status_message("Cacher: Snippets loaded")
    except IOError:
        util.prompt_user_setup()
    except urllib.error.HTTPError:
        return
    except ValueError:
        util.show_credentials_parse_error()


def set_store(data):
    set_snippets(data)
    set_teams(data)


def set_snippets(data):
    store = util.store()
    store.set("personal_library", data["personalLibrary"])

    labels = data["personalLibrary"]["labels"]
    personal_snippets = list(
        map(
            lambda s: snippet_with_label(s, labels, None),
            data["personalLibrary"]["snippets"]
        )
    )

    team_snippets = []

    for team in data["teams"]:
        labels = team["library"]["labels"]
        team_snippets += list(
            map(
                lambda s: snippet_with_label(s, labels, team),
                team["library"]["snippets"]
            )
        )

    store.set("snippets", personal_snippets + team_snippets)


def snippet_with_label(snippet, labels, team):
    copy = dict()
    copy.update(snippet)

    copy["team"] = team
    copy["labels"] = snippet_labels(labels, snippet)
    return copy


def snippet_labels(labels, snippet):
    snip_labels = []

    for label in labels:
        has_snippet = False
        for label_snippet in label["snippets"]:
            if label_snippet["guid"] == snippet["guid"]:
                has_snippet = True
        if has_snippet:
            snip_labels.append(label["title"])

    return snip_labels


def set_teams(data):
    util.store().set("teams", data["teams"])
    teams_editable = list(filter(
        lambda team: team["userRole"] == "owner" or team["userRole"] == "manager" or team["userRole"] == "member",
        data["teams"]
    ))
    util.store().set("teams_editable", teams_editable)
