from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    if len(args) != 1:
        print(f"USAGE: thick-denim run {__file__} ISSUE-01234")
        raise SystemExit(1)
    client = JiraClient(config, "goodscloud")

    key = args[0]
    issue = client.get_issue(key)

    print(issue.format_robust_table())
    issue_transitions = client.get_issue_transitions(issue)
    print(issue_transitions.format_pretty_table())
