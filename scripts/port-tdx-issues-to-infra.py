import pendulum
import logging
from typing import List
from humanfriendly.text import pluralize
from humanfriendly.prompts import prompt_for_confirmation
from thick_denim.config import ThickDenimConfig
from thick_denim.errors import ThickDenimError
from thick_denim.base import store_models, load_models, slugify
from thick_denim.networking.jira.client import JiraClient, JiraClientException
from thick_denim.networking.jira.models import JiraIssue
from thick_denim.networking.jira.models import JiraIssueType
from thick_denim.networking.jira.models import JiraProject
from thick_denim.logs import UIReporter

ui = UIReporter("Issue Transferrer")
logger = logging.getLogger(__name__)


class by:
    "this class is just a namespace to group all filter functions."

    @staticmethod
    def updated_within_last_2_months(issue: JiraIssue):
        today = pendulum.today()
        age_in = today - issue.updated_at
        return age_in.months <= 2

    @staticmethod
    def status_is_not_done(issue: JiraIssue):
        return (
            "".join(str(issue.status_name).lower().split()).strip() != "done"
        )


def get_source_issues_by_epic(client: JiraClient, source_project: JiraProject):
    """retrieves all issues from a project and returns them
    in a dictionary where the key is the epic issue and the
    value is a a lit of issues"""

    print(
        f"retrieving list of all issues in source project: {source_project.key}"
    )
    source_issues = client.get_issues_from_project(source_project.key).filter(
        by.status_is_not_done
    )
    print(f"filtering only issues active in the last 2 months")
    issues_active_within_last_2_months = source_issues.filter(
        by.updated_within_last_2_months
    )

    print(f"gathering data about unassigned issues")
    issues_without_assignee = issues_active_within_last_2_months.filter(
        lambda issue: not issue.assignee_key
    )
    print(f"gathering data about owned issues")
    owned_issues = issues_active_within_last_2_months.filter(
        lambda issue: issue.assignee_key
    )
    print(f"extracting epics from list of issues")

    epics = issues_active_within_last_2_months.filter(
        lambda issue: issue.issue_type_name.lower() == "epic"
    )
    TASKS_BY_EPIC = {}
    for epic in epics:
        # print(f'\t retrieving issues from epic {epic.key}: {epic.summary} (active within last 2 months)')
        issues_from_epic = client.get_issues_with_jql(
            f"parent = {epic.id}"
        ).filter(by.updated_within_last_2_months)
        if issues_from_epic:
            TASKS_BY_EPIC[epic] = issues_from_epic

    if not TASKS_BY_EPIC:
        print(f"could not find issues for epics: {epics}")
        raise SystemExit(1)

    print(f"Summary for TDX:\n")
    print(
        f"{pluralize(len(issues_active_within_last_2_months), 'issue')} active within the last 2 months"
    )
    print(f"{pluralize(len(owned_issues), 'issue')} with an owner")
    print(f"{pluralize(len(issues_without_assignee), 'unassigned issue')}")
    print(f"{pluralize(len(epics), 'epic')} ")
    print(epics.format_pretty_table())

    return TASKS_BY_EPIC


def get_matching_issue_type(
    issue_type_name: str, issue_types: List[JiraIssueType]
):
    """takes a list of issue types and extract the one that matches the given issue type name.
    this function is used for extracting the correct issue type id before creating an issue in the target project.
    """
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


def transfer_tasks_without_epic(client, source_project, target_project):
    """this function contains a loop that iterate over all epics in the
    source project, then a nested loop of all issues inside of this
    epic, then it clones each epic and child issue to the target
    project by prompting user to confirm the creation on each loop.
    """
    issue_types = client.get_issue_types(target_project)
    source_issues_without_epic = (
        client.get_issues_from_project(source_project.key)
        .filter(lambda issue: not issue.parent)
        .filter(by.updated_within_last_2_months)
    )

    for source_issue in source_issues_without_epic:
        fields = {"description": source_issue.description}
        fields.update(newstore_apps_fields)

        for important_key in ["attachment", "components"]:
            important_value = source_issue.get(important_key)
            if important_value:
                fields[important_key] = important_value

        if source_issue.assignee_key:
            fields["assignee"] = source_issue.assignee

        # if source_issue.reporter_key:
        #     fields["reporter"] = source_issue.reporter

        new_summary = f"{source_issue.summary} (former {source_issue.key})"
        print(
            f'transfering epic-less {source_issue.key} "{source_issue.summary}" to {target_project.key}'
        )
        target_task_type = get_matching_issue_type(
            source_issue.issue_type_name, issue_types
        )
        candidate_issues = client.get_issues_by_summary(
            source_issue.summary, project=target_project
        )
        target_issue = candidate_issues and candidate_issues[0]

        if target_issue:
            print(f"\033[1;34mIssue already exists: {target_issue.key}\033[0m")
            continue

        try:
            target_issue = client.get_or_create_issue_by_summary(
                new_summary,
                project=target_project,
                issue_type=target_task_type,
                fields=fields,
            )
        except JiraClientException as e:
            logger.exception(f"failed to transfer {new_summary!r}: {e}")
            continue

        if target_issue:
            print(
                f"\033[1;32mtransfered task {target_issue.key}: {target_issue.summary}\033[0m"
            )


def transfer_epics_and_subtasks_to_another_project(
    client, source_project, target_project, TASKS_BY_EPIC, issue_types
):
    epics = JiraIssue.List(list(TASKS_BY_EPIC.keys()))

    for epic in epics.filter_by("summary", "*Toolbelt*"):
        candidate_epics = client.get_issues_by_summary(
            epic.summary, project=target_project
        )
        if candidate_epics:
            target_epic = candidate_epics[0]
            print(f"\033[1;34mEpic already exists on target: {target_epic.key} {target_epic.summary!r}\033[0m")

        else:
            print(
                f"\033[1;34mtransfering Epic {epic.key}: {epic.summary} to project {target_project.key}: {target_project.name}\033[0m"
            )
            fields = {"description": epic.description}

            for important_key in ["attachment", "components"]:
                important_value = epic.get(important_key)
                if important_value:
                    fields[important_key] = important_value

            if epic.assignee_key:
                fields["assignee"] = epic.assignee

            # if epic.reporter_key:
            #     fields["reporter"] = epic.reporter

            target_task_type = get_matching_issue_type(
                epic.issue_type_name, issue_types
            )
            if not prompt_for_confirmation(f"Confirm ?"):
                continue

            if target_project.key == 'NA':
                # NewStore Apps project has a custom field for the epic "link", the value must be the epic key.
                fields["customfield_10009"] = epic.key

            new_epic_summary = f"{epic.summary} (former {epic.key})"
            target_epic = client.get_or_create_issue_by_summary(
                new_epic_summary,
                project=target_project,
                issue_type=target_task_type,
                fields=fields,
            )
            if target_epic:
                print(f"\033[1;32mcreated Epic {target_epic.key}: {target_epic.summary}\033[0m")
            else:
                raise ThickDenimError(f'failed to create epic {new_epic_summary!r}')

        for source_issue in TASKS_BY_EPIC[epic]:
            fields = {"description": source_issue.description}
            fields.update(newstore_apps_fields)
            for important_key in ["attachment", "components"]:
                important_value = source_issue.get(important_key)
                if important_value:
                    fields[important_key] = important_value

            if source_issue.assignee_key:
                fields["assignee"] = source_issue.assignee

            # if source_issue.reporter_key:
            #     fields["reporter"] = source_issue.reporter

            candidate_issues = client.get_issues_by_summary(
                source_issue.summary, project=target_project
            )
            target_issue = candidate_issues and candidate_issues[0]

            if target_issue:
                client.link_issues(source_issue, target_issue, 'Cloners')

                print(f"\033[1;34mIssue already exists: {target_issue.key} {target_issue.summary!r}\033[0m")
            else:
                print(
                    f'\033[1;33mtransfering {source_issue.key} "{source_issue.summary}" to {target_project.name}\033[0m'
                )
                target_task_type = get_matching_issue_type(
                    "Tech Story", issue_types
                )
                if not prompt_for_confirmation(f"Confirm ?"):
                    continue

                try:
                    target_issue = client.get_or_create_issue_by_summary(
                        f"{source_issue.summary} (former {source_issue.key})",
                        project=target_project,
                        issue_type=target_task_type,
                        fields=fields,
                    )
                except JiraClientException as e:
                    print(
                        f"\033[1;31mfailed to transfer task{source_issue.key} {source_issue.summary!r}: {e}\033[0m"
                    )
                    raise SystemExit(1)

                if target_issue:
                    print(
                        f"\t\t\033[1;32mtransfered task {target_issue.key}: {target_issue.summary}\033[0m"
                    )

            linked_summaries = [link.target.summary for link in source_issue.issue_links]
            if target_issue.summary not in linked_summaries:
                print(f'\t\033[1;36mcreating link exists between issues {source_issue.key} and {target_issue.key}')
                client.link_issues(
                    source_issue,
                    target_issue,
                    f'ported from {source_project.key} through a script',
                )


newstore_apps_fields = {
    # 'customfield_14191': { # TST project only
    #     'id': '14539',
    #     'self': 'https://goodscloud.atlassian.net/rest/api/3/customFieldOption/14539',
    #     'value': '#team-infrastructure'
    # },
    "labels": ["infra-w9"],
    # 'status': ?
    "customfield_10602": {  # NA project only
        "id": "10315",
        "self": "https://goodscloud.atlassian.net/rest/api/3/customFieldOption/10315",
        "value": "#infrastructure",
    },
    'customfield_13900': {
        'id': '14003',
        'self': 'https://goodscloud.atlassian.net/rest/api/3/customFieldOption/14003',
        'value': 'S'
    },
}


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    source_project = client.get_project("TDX")
    target_project = client.get_project("NA")

    print(f"retrieving issue types for project {source_project.key}")
    issue_types = client.get_issue_types(target_project)
    if not issue_types:
        print(
            f"no issue types could be retrieved from {target_project.key}: {target_project.name}"
        )
        raise SystemExit(1)

    TASKS_BY_EPIC = get_source_issues_by_epic(client, source_project)

    print(f"beginning to port issues to project {target_project.name} ({target_project.key})")
    # transfer_tasks_without_epic(client, source_project, target_project)
    try:
        transfer_epics_and_subtasks_to_another_project(
            client, source_project, target_project, TASKS_BY_EPIC, issue_types
        )
    except KeyboardInterrupt:
        print("\rUser cancelled (Control-C)")
        raise SystemExit(130)
