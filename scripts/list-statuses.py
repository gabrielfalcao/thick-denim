from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    project = client.get_project("NA")
    statuses = client.get_issue_statuses(project)
    print(statuses.format_pretty_table())
