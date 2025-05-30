from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    if len(args) == 0:
        print("issues must be passed as arguments")
        raise SystemExit(1)

    for key in args:
        issue = client.get_issue(key)
        if not issue:
            print(f"issue not found: {key}")
            raise SystemExit(1)

        if client.delete_issue(issue):
            print(f"deleted: {key}")
