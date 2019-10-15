import pendulum
from typing import List
from humanfriendly.text import pluralize
from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient
from thick_denim.networking.jira.models import JiraIssue


class by:
    @staticmethod
    def updated_within_last_2_months(issue):
        today = pendulum.today()
        age_in = today - issue.updated_at
        return age_in.months <= 2


def pluralize_issues(items: List[JiraIssue], singular: str = "issue") -> str:
    count = len(items)
    return pluralize(count, singular)


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    all_tst_issues = client.get_issues_from_project("TST")
    print(all_tst_issues.format_pretty_table())
