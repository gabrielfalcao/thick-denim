import pendulum
from typing import List
from humanfriendly.text import pluralize
from thick_denim.config import ThickDenimConfig
from thick_denim.base import store_models, load_models
from thick_denim.networking.jira.client import JiraClient
from thick_denim.networking.jira.models import JiraIssue


def get_issues_from_cache_or_api(
    client: JiraClient, project_key: str, update_cache: bool = False
):
    issues_cache_filename = f"{project_key}-issues.json"

    if update_cache:
        issues = []
    else:
        issues = load_models(issues_cache_filename, JiraIssue)

    if not issues:
        issues = client.get_issues_from_project("TDX")
        store_models(issues, issues_cache_filename)

    return issues


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

    all_tdx_issues = get_issues_from_cache_or_api(
        client, project_key="TDX", update_cache=True
    )
    issues_active_within_last_2_months = all_tdx_issues.filter(
        by.updated_within_last_2_months
    )

    issues_without_assignee = issues_active_within_last_2_months.filter(
        lambda issue: not issue.assignee_key
    )
    owned_issues = issues_active_within_last_2_months.filter(
        lambda issue: issue.assignee_key
    )
    epics = issues_active_within_last_2_months.filter(
        lambda issue: issue.issue_type_name.lower() == "epic"
    )

    print(f"Summary for TDX:\n")
    print(
        f"{pluralize_issues(issues_active_within_last_2_months)} active within the last 2 months"
    )
    print(f"{pluralize_issues(owned_issues)} with an owner")
    print(f"{pluralize_issues(issues_without_assignee, 'unassigned issue')}")
    print(f"{pluralize_issues(epics, 'epic')} ")
    print(epics.format_pretty_table())
