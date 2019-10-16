import pendulum
import logging
import json
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
    def not_done_yet(issue: JiraIssue):
        return issue.status_name != 'Done'

    @staticmethod
    def not_an_epic(issue: JiraIssue):
        return issue.issue_type_name != 'Epic'


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


def transfer_issues_without_epic_to_another_project(
        client, source_project, target_project, issue_types,
):
    issues_without_epic = client.get_issues_from_project(source_project).filter(
        lambda issue: not issue.parent
    ).filter(
        by.updated_within_last_2_months
    ).filter(
        by.not_an_epic
    ).sorted_by(
        'created_at'
    ).sorted_by(
        'updated_at'
    )
    for source_issue in issues_without_epic:
        if source_issue.status_name.lower() == 'done':
            print(f'\033[1;30mskipping issue {source_issue.key} {source_issue.summary!r} because has status {source_issue.status_name}\033[0m')
            continue

        if isinstance(source_issue.description, dict):
            new_description = source_issue.description.copy()
        else:
            new_description = {
                'content': [],
                'type': 'doc',
                'version': 1
            }

        new_description['content'].extend([
            {'type': 'rule'},
            {
                'content': [{
                    'text': f'Epic: No Epic',
                    'type': 'text'
                }],
                'type': 'paragraph'
            },
            {
                'type': 'paragraph',
                'content': [
                    {
                        'text': f'Cloned from {source_issue.key}',
                        'type': 'text'
                    }, {
                        'marks': [{
                            'attrs': {
                                'href': source_issue.url,
                            },
                            'type': 'link'
                        }],
                        'text': source_issue.key,
                        'type': 'text'
                    }
                ],
            },
            {
                'content': [{
                    'text': f'Original status: {source_issue.status_name}',
                    'type': 'text'
                }],
                'type': 'paragraph'
            },
        ])
        fields = {"description": new_description}

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
            print(f"\033[1;34mIssue already exists: {target_issue.key} {target_issue.summary!r}\033[0m")
        else:
            target_task_type = get_matching_issue_type(
                "Tech Story", issue_types
            )
            print(source_issue.format_robust_table())
            if not prompt_for_confirmation(f'Do you want to transfer \033[1;32m{source_issue.key}\033[0m to {target_project.name} ({target_project.key})?'):
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
                    f"\033[1;31mfailed to transfer issue {source_issue.key} {source_issue.summary!r}: {e}\033[0m"
                )
                raise SystemExit(1)

            if target_issue:
                print(
                    f"\033[1;32mtransfered task {target_issue.key}: {target_issue.summary}\033[0m"
                )

        linked_summaries = [link.target.summary for link in target_issue.issue_links]
        if source_issue.summary not in linked_summaries:
            print(f'\033[1;36mcreating link exists between issues {source_issue.key} and {target_issue.key}')
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
    "labels": ["infra-w9", "devx", "devx-epicless", "ported-by-script"],
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

    print(f"beginning to port issues to project {target_project.name} ({target_project.key})")
    try:
        transfer_issues_without_epic_to_another_project(
            client, source_project, target_project, issue_types,
        )
    except KeyboardInterrupt:
        print("\rUser cancelled (Control-C)")
        raise SystemExit(130)
