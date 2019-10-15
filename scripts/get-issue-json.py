import json
from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    if len(args) != 1:
        print(f"USAGE: thick-denim run {__file__} ISSUE-01234")
        raise SystemExit(1)

    key = args[0]
    issue = client.get_issue(key)
    print(json.dumps(issue.to_dict(), indent=4))
