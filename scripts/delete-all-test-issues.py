from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient
from thick_denim.networking.jira.models import JiraProject


def get_test_project(client):
    test_project = client.get_project("TST")
    if not test_project:
        print(f"test project was not found")
        raise SystemExit(1)

    return test_project


def delete_issues_matching_summary(
    client: JiraClient, project: JiraProject, summary_glob: str
):
    for issue in client.get_issues_by_summary(summary_glob, project=project):
        print(
            f"\033[1;31mdeleting issue: \033[1;33m{issue.key}: \033[1;37m{issue.summary}\033[0m"
        )
        client.delete_issue(issue)


def main(config: ThickDenimConfig):
    client = JiraClient(config, "goodscloud")

    project = get_test_project(client)

    delete_issues_matching_summary(client, project, f"Test epic #1")
    delete_issues_matching_summary(
        client, project, f"Basic Issue created via API*"
    )
    delete_issues_matching_summary(client, project, f"Test")

    for issue in client.get_issues_from_project(project.id):
        print(
            f"\033[1;31mdeleting issue: \033[1;33m{issue.key}: \033[1;37m{issue.summary}\033[0m"
        )
        client.delete_issue(issue)
