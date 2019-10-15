# import pendulum
# from collections import defaultdict
from thick_denim.config import ThickDenimConfig
# from thick_denim.base import store_models, load_models
from thick_denim.networking.jira.client import JiraClient, ui
from thick_denim.networking.jira.models import (

    JiraProject,
    # JiraIssue,
    JiraIssueType,
)
from thick_denim.logs import UIReporter


ui = UIReporter("Create Test Issues")


def get_test_project(client):
    test_project = client.get_project('TST')
    if not test_project:
        print(f"test project was not found")
        raise SystemExit(1)

    return test_project


def delete_issues_matching_summary(client: JiraClient, project: JiraProject, summary_glob: str):
    for issue in client.get_issues_by_summary(
        summary_glob,
        project=project,
    ):
        ui.debug(f'\033[1;31mdeleting issue: {issue!r}\033[0m')
        client.delete_issue(issue)


def main(config: ThickDenimConfig):
    client = JiraClient(config, "goodscloud")

    project = get_test_project(client)

    issue_types = JiraIssueType.List(filter(
        lambda i: i.project_id == project.id,
        client.get_issue_types(project)
    ))

    epic_type = issue_types.filter_by('name', 'Epic')[0]
    task_type = issue_types.filter_by('name', 'Task')[0]

    delete_issues_matching_summary(
        client, project, f'Test epic #1')
    delete_issues_matching_summary(
        client, project, f'Basic Issue created via API*')
    delete_issues_matching_summary(
        client, project, f'Test')

    description = f'created by gfalcao@newstore.com for project TST'

    if epic_type.name != 'Epic':
        print(f'issue_type should be Epic: {epic_type}')
        raise SystemExit(1)

    test_epic = client.get_or_create_issue_by_summary(
        f'Test Epic #1',
        project,
        issue_type=epic_type,
        basic_description=description
    )
    if not test_epic:
        print('failed to get or create epic')
        raise SystemExit(1)

    print(f"created epic {test_epic.key}: {test_epic.summary!r}")

    if task_type.name != 'Task':
        print(f'issue_type should be Task: {task_type}')
        raise SystemExit(1)

    test_task = client.get_or_create_issue_by_summary(
        f'Test Task #1 created via api',
        project,
        parent=test_epic,
        issue_type=task_type,
        basic_description=description
    )

    print(f"created task {test_task.key}: {test_task.summary!r}")
    print(f"\tunder as child of epic task {test_epic.key}: {test_epic.summary!r}")
