import pendulum
import logging
from typing import List
from humanfriendly.text import pluralize
from thick_denim.config import ThickDenimConfig
from thick_denim.base import store_models, load_models, slugify
from thick_denim.networking.jira.client import JiraClient, JiraClientException
from thick_denim.networking.jira.models import JiraIssue
from thick_denim.networking.jira.models import JiraIssueType
from thick_denim.networking.jira.models import JiraProject
from thick_denim.logs import UIReporter

ui = UIReporter("Issue Transferrer")
logger = logging.getLogger(__name__)


def delete_all_issues_from_project(client: JiraClient, project: JiraProject):
    all_issues = client.get_issues_from_project(project.id, max_pages=-1)
    epics = all_issues.filter(lambda i: i.issue_type_name == "Epic")
    for issue in epics:
        if client.delete_issue(issue):
            ui.debug(f"\033[1;31mdeleted {issue}\033[0m")
    for issue in client.get_issues_from_project(project.id, max_pages=-1):
        if client.delete_issue(issue):
            ui.debug(f"\033[1;31mdeleted {issue}\033[0m")


def get_issues_by_project_from_cache_or_api(
    client: JiraClient, project_key: str, update_cache: bool = False
):
    issues_cache_filename = f"{project_key}-issues.json"

    if update_cache:
        issues = []
    else:
        issues = load_models(issues_cache_filename, JiraIssue)

    if not issues:
        issues = client.get_issues_from_project(project_key, max_pages=-1)
        store_models(issues, issues_cache_filename)

    return issues


def get_issues_by_jql_from_cache_or_api(
    client: JiraClient, jql: str, update_cache: bool = False
):
    issues_cache_filename = f"jql-{slugify(jql)}-issues.json"

    if update_cache:
        issues = []
    else:
        issues = load_models(issues_cache_filename, JiraIssue)

    if not issues:
        issues = client.get_issues_with_jql(jql, max_pages=-1)
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


def get_source_issues_by_epic(client: JiraClient, source_project: JiraProject):

    UPDATE_CACHE = True
    source_project = client.get_project("TDX")

    source_issues = get_issues_by_project_from_cache_or_api(
        client, project_key=source_project.key, update_cache=UPDATE_CACHE
    )
    issues_active_within_last_2_months = source_issues.filter(
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
    TASKS_BY_EPIC = {}
    for epic in epics:
        issues_from_epic = get_issues_by_jql_from_cache_or_api(
            client, jql=f"parent = {epic.id}", update_cache=UPDATE_CACHE
        )
        if issues_from_epic:
            TASKS_BY_EPIC[epic] = issues_from_epic

    if not TASKS_BY_EPIC:
        print(f"could not find issues for epics: {epics}")
        raise SystemExit(1)

    print(f"Summary for TDX:\n")
    print(
        f"{pluralize_issues(issues_active_within_last_2_months)} active within the last 2 months"
    )
    print(f"{pluralize_issues(owned_issues)} with an owner")
    print(f"{pluralize_issues(issues_without_assignee, 'unassigned issue')}")
    print(f"{pluralize_issues(epics, 'epic')} ")
    print(epics.format_pretty_table())

    return TASKS_BY_EPIC


def get_matching_issue_type(
    issue_type_name: str, issue_types: List[JiraIssueType]
):
    types = issue_types.filter_by("name", issue_type_name)
    if not types:
        if not issue_types:
            raise RuntimeError(
                f"issue_types argument cannot be empty: {issue_type_name}"
            )
        else:
            raise RuntimeError(
                f"no matching issue type {issue_type_name!r} in {issue_types}"
            )
    target_task_type = types[0]
    if target_task_type.name != issue_type_name:
        raise RuntimeError(
            f"issue_type should be {issue_type_name}: {target_task_type}"
        )

    return target_task_type


def main(config: ThickDenimConfig):
    client = JiraClient(config, "goodscloud")
    target_project = client.get_project("TST")
    source_project = client.get_project("TDX")
    delete_all_issues_from_project(client, target_project)

    TASKS_BY_EPIC = get_source_issues_by_epic(client, source_project)

    transfer_tasks_without_epic(client, source_project, target_project)
    transfer_epics_and_subtasks_to_another_project(
        client, source_project, target_project, TASKS_BY_EPIC
    )


def transfer_tasks_without_epic(client, source_project, target_project):
    issue_types = client.get_issue_types(target_project)
    source_issues_without_epic = client.get_issues_from_project(
        source_project.key
    ).filter(lambda issue: not issue.parent)
    for source_task in source_issues_without_epic:
        fields = {"description": source_task.description}
        for important_key in ["attachment", "components"]:
            important_value = source_task.get(important_key)
            if important_value:
                fields[important_key] = important_value

        if source_task.assignee_key:
            fields["assignee"] = source_task.assignee

        if source_task.reporter_key:
            fields["reporter"] = source_task.reporter

        new_summary = f"{source_task.summary} (former {source_task.key})"
        print(
            f'transfering epic-less {source_task.key} "{source_task.summary}" to {target_project.key}'
        )
        target_task_type = get_matching_issue_type(
            source_task.issue_type_name, issue_types
        )
        try:
            transferred_task = client.get_or_create_issue_by_summary(
                new_summary,
                project=target_project,
                issue_type=target_task_type,
                fields=fields,
            )
        except JiraClientException as e:
            logger.exception(f"failed to transfer {new_summary!r}: {e}")
            continue

        if transferred_task:
            print(
                f"\t\ttransfered task {transferred_task.key}: {transferred_task.summary}"
            )


def transfer_epics_and_subtasks_to_another_project(
    client, source_project, target_project, TASKS_BY_EPIC
):
    issue_types = client.get_issue_types(target_project)
    epics = JiraIssue.List(list(TASKS_BY_EPIC.keys()))

    for epic in epics:
        existent_in_target = client.get_issues_by_summary(
            epic.summary, project=target_project
        )
        if existent_in_target:
            print(f"\tEpic already exists on target: {existent_in_target}")
            continue

        print(
            f"transfering Epic {epic.key}: {epic.summary} to project {target_project.key}: {target_project.name}"
        )
        fields = {"description": epic.description}
        for important_key in ["attachment", "components"]:
            important_value = epic.get(important_key)
            if important_value:
                fields[important_key] = important_value

        if epic.assignee_key:
            fields["assignee"] = epic.assignee

        if epic.reporter_key:
            fields["reporter"] = epic.reporter

        target_task_type = get_matching_issue_type(
            epic.issue_type_name, issue_types
        )
        target_epic = client.get_or_create_issue_by_summary(
            f"{epic.summary} (former {epic.key})",
            project=target_project,
            issue_type=target_task_type,
            fields=fields,
        )
        if target_epic:
            print(f"\tcreated Epic {target_epic.key}: {target_epic.summary}")
            for source_task in TASKS_BY_EPIC[epic]:
                fields = {"description": source_task.description}
                for important_key in ["attachment", "components"]:
                    important_value = source_task.get(important_key)
                    if important_value:
                        fields[important_key] = important_value

                if source_task.assignee_key:
                    fields["assignee"] = source_task.assignee

                if source_task.reporter_key:
                    fields["reporter"] = source_task.reporter

                print(
                    f'\t\ttransfering {source_task.key} "{source_task.summary}" to {target_project.key}'
                )
                target_task_type = get_matching_issue_type(
                    source_task.issue_type_name, issue_types
                )
                try:
                    transferred_task = client.get_or_create_issue_by_summary(
                        f"{source_task.summary} (former {source_task.key})",
                        project=target_project,
                        issue_type=target_task_type,
                        fields=fields,
                    )
                except JiraClientException as e:
                    print(
                        f"\033[1;31mfailed to transfer task{source_task.key} {source_task.summary!r}: {e}\033[0m"
                    )
                if transferred_task:
                    print(
                        f"\t\ttransfered task {transferred_task.key}: {transferred_task.summary}"
                    )
