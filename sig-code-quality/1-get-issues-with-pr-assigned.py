from thick_denim.config import ThickDenimConfig
from thick_denim.base import store_models, load_models
from thick_denim.networking.jira.models import JiraIssue
from thick_denim.networking.jira.client import JiraClient


def query_and_cache_issues(
    client: JiraClient, update_cache: bool = False
):
    issues_cache_filename = f"inventory-team-todo-and-in-progress-issues.json"

    issues = load_models(issues_cache_filename, JiraIssue)

    if not update_cache and issues:
        return issues

    devteam = '#inventory'
    jql_parts = [
        f"project = NA",
        # f'"Dev Team" = "{devteam}"',
        f'"Status" IN ("To Do", "In Progress")',
        # f'"Development" IS NOT NULL',
    ]
    jql = " AND ".join(jql_parts)

    issues = client.get_issues_with_jql(jql)
    store_models(issues, issues_cache_filename)

    return issues


def contains_pr_reference(issue: JiraIssue):
    if not issue.development:
        return False

    import ipdb;ipdb.set_trace()


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    issues = query_and_cache_issues(client, update_cache=False)
    issues = issues.filter(contains_pr_reference)
    print(issues.format_pretty_table())
