from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    project = client.get_project("NA")
    issue_types = client.get_issue_link_types(project)
    print(issue_types.format_pretty_table())
