import os.path
import json

home = os.path.expanduser("~")
cacher_dir = os.path.join(home, ".cacher")
credentials_file = os.path.join(cacher_dir, "credentials.json")


def credentials_exist():
    return os.path.exists(credentials_file)


def get_credentials():
    if credentials_exist():
        with open(credentials_file) as creds_file:
            return json.load(creds_file)
    else:
        return None


def save_credentials(key, token):
    if not os.path.exists(cacher_dir):
        os.mkdir(cacher_dir)

    with open(credentials_file, "w") as file:
        content = {"key": key, "token": token}
        with open(credentials_file, "w") as creds_file:
            json.dump(content, creds_file)
