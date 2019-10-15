from humanfriendly.prompts import prompt_for_confirmation
from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    if len(args) != 2:
        print("USAGE: thick-denim run {__file__} FROM_ISSUE TO_ISSUE")
        raise SystemExit(1)

    source_issue_key, target_issue_key = args

    source_issue = client.get_issue(source_issue_key)
    target_issue = client.get_issue(target_issue_key)

    print(f'This script will link {source_issue.key} {source_issue.summary!r} as cloned by {target_issue.key}: {target_issue.summary!r}')
    if prompt_for_confirmation('Confirm ?'):
        client.link_issues(source_issue, target_issue, 'Cloners')
