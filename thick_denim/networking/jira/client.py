# -*- coding: utf-8 -*-
"""
contains utilities to make calls to the Jira API
"""
import json
import requests
import logging
from typing import List
from thick_denim.errors import ThickDenimError
from thick_denim.config import ThickDenimConfig
from thick_denim.logs import UIReporter
from .models import JiraIssue, JiraProject, JiraIssueChangelog, JiraIssueType


ui = UIReporter("Jira Client")


logger = logging.getLogger(__name__)


class JiraClientException(ThickDenimError):
    """raised within the JiraClient class"""


class JiraClientHttpException(JiraClientException):
    """raised when Jira API returns a non 2xx response"""

    def __init__(self, url, data, status, message):
        message = f"{message}.\n{status} for url {url}: {data}"
        super().__init__(message)


class TooManyIssuesMatched(JiraClientException):
    def __init__(self, criteria: str, issues: List[JiraIssue]):
        self.criteria = criteria
        self.issues = issues
        self.total_issues = len(issues)
        super().__init__(
            f"too many issues matching the criteria "
            f"{criteria!r} ({self.total_issues}): {issues}"
        )


# JIRA Cloud Platform API docs:
# https://developer.atlassian.com/cloud/jira/platform/rest/v3/

# jira:
#   token: SOMETOKEN  # get one at https://id.atlassian.com/manage/api-tokens
#   server: https://goodscloud.atlassian.net


class JiraClient(object):
    """client to the jira api that uses the personal token from newstore
    config.
    """

    def __init__(
        self, config: ThickDenimConfig, account_name: str = "goodscloud"
    ):
        self.config = config
        self.jira_server = config.get_jira_server(account_name)
        self.jira_email = config.get_jira_email(account_name)
        self.jira_token = config.get_jira_personal_token(account_name)
        self.http = requests.Session()
        self.http.auth = (self.jira_email, self.jira_token)
        self.http.headers.update(
            {"Bearer": f"{self.jira_token}", "Accept": "application/json"}
        )

    def api_url(self, path: str):
        return f'{self.jira_server}/rest/api/3/{path.lstrip("/")}'

    def get_issue(self, issue_key):
        logger.debug(f"retrieving issue {issue_key}")
        params = {
            "fields": "*all",
            "expand": ["names", "schema", "operations"],
            "fieldsByKeys": False,
        }
        response = self.http.get(
            self.api_url(f"/issue/{issue_key}"),
            params=params,
        ).json()
        data = response["fields"]
        names = response.get("names")
        issue = JiraIssue(data)
        if names:
            issue = issue.with_updated_field_names(names)

        return issue

    def get_issues_from_project(self, id_or_key, max_pages: int = -1):
        return self.get_issues_with_jql(f"project = {id_or_key}")

    def get_issues_with_jql(self, jql: str, max_pages: int = -1):
        # https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-search-post
        params = {
            "expand": ["names", "schema", "operations"],
            "jql": jql,
            "maxResults": 100,
            "fieldsByKeys": False,
            "fields": "*all",
            "startAt": 0,
        }
        items, names = self.request_with_pages(
            "/search",
            f"retrieving issues for jql: {jql}",
            max_pages=max_pages,
            params=params,
            items_key="issues",
        )
        return JiraIssue.Set(
            map(
                lambda issue: issue.with_updated_field_names(names),
                JiraIssue.Set(items),
            )
        )

    def get_issues_by_summary(
        self, summary: str, project: JiraProject = None, max_pages: int = -1
    ):
        parts = [f'summary ~ "{summary}"']
        if project:
            parts.append(f"project = {project.id}")

        jql = " AND ".join(parts)
        return self.get_issues_with_jql(jql)

    def get_changelogs_from_issue(self, id_or_key, max_pages: int = -1):
        # https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-issue-issueIdOrKey-changelog-get
        params = {"maxResults": 100, "startAt": 0}
        logger.debug(f"retrieving changelog from issue {id_or_key}")
        items, names = self.request_with_pages(
            f"/issue/{id_or_key}/changelog",
            f"retrieving changelog from issue {id_or_key}",
            max_pages=max_pages,
            params=params,
        )
        return JiraIssueChangelog.Set(items)

    def request_with_pages(
        self,
        url,
        message: str,
        max_pages: int,
        params: dict = {},
        items_key: str = "values",
    ):
        current_page = 1
        next_url = self.api_url(url)
        msg = f"{message} (page {current_page}) url: {next_url} (startAt: 0)"
        ui.debug(msg)
        response = self.http.get(next_url, params=params)
        data = self.validated_response(url, response, message)
        next_url = data.get("nextPage", next_url)
        items = data[items_key]
        total = data.get("total", 0)

        should_request_next_page = (
            lambda: (max_pages < 0 and len(items) <= total)
            or current_page <= max_pages
        )
        field_names = data.get("names", {})
        while items and should_request_next_page():
            start_at = len(items) - 1
            params["startAt"] = start_at
            current_page += 1
            msg = f"{message} (page {current_page}) url: {next_url} (startAt: {start_at})"
            response = self.http.get(next_url, params=params)
            data = self.validated_response(next_url, response, msg)
            next_url = data.get("nextPage", next_url)
            items.extend(data[items_key])
            ui.debug(msg)

            if data.get("isLast"):
                break

        return items, field_names

    def get_projects(self, max_pages: int = 1):
        logger.debug(f"retrieving all projects")
        params = {"maxResults": 50, "startAt": 0, "orderBy": "key"}

        items, names = self.request_with_pages(
            "/project/search",
            "retrieving projects",
            max_pages=max_pages,
            params=params,
        )
        return JiraProject.Set(items)

    def get_issue_types(self, project: JiraProject, max_pages: int = 1):
        logger.debug(f"retrieving all issue types")
        params = {"maxResults": 50, "startAt": 0, "orderBy": "key"}

        response = self.http.get(self.api_url("/issuetype"), params=params)
        types = response.json()

        return JiraIssueType.Set(types).filter(
            lambda i: i.project_id == project.id
        )

    def get_project(self, id_or_key):
        logger.debug(f"retrieving project {id_or_key}")
        data = self.http.get(self.api_url(f"/project/{id_or_key}")).json()
        return JiraProject(data)

    def validated_response(
        self, url, response, message, valid_statuses=(200, 201, 202, 203, 204)
    ):
        status = response.status_code

        if status in valid_statuses:
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data
        else:
            data = response.text

        raise JiraClientHttpException(url, data, status, message)

    def create_issue(
        self,
        summary: str,
        project: JiraProject,
        issue_type: JiraIssueType,
        description: str,
        parent: JiraIssue = None,
        **fields,
    ):
        message = f"creating issue {summary!r} of type {issue_type} in project {project}: {description}"
        logger.info(message)
        required_fields = {
            "summary": summary,
            "issuetype": issue_type.to_dict(),
            "project": project.to_dict(),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"text": description, "type": "text"}],
                    }
                ],
            },
        }
        merged_fields = required_fields.copy()
        merged_fields.update(fields)
        update_fields = {}
        if parent:
            if not parent.id:
                raise JiraClientException(
                    f"cannot create issue with parent missing id: {parent}"
                )

            merged_fields["parent"] = parent.to_dict()

        payload = json.dumps({"update": update_fields, "fields": merged_fields})
        url = self.api_url("/issue")
        response = self.http.post(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        meta = self.validated_response(url, response, message)
        id = meta.get("id")
        key = meta.get("key")

        fresh = self.get_issue(id or key)
        if fresh:
            fresh.update(meta)
            return fresh

        import ipdb;ipdb.set_trace()
        return JiraIssue(meta)

    def get_issue_by_summary(self, summary: str) -> JiraIssueType:
        existing_issues = self.get_issues_by_summary(summary)
        total_issues = len(existing_issues)
        if total_issues == 1:
            return existing_issues[0]
        elif total_issues > 1:
            import ipdb

            ipdb.set_trace()
            raise TooManyIssuesMatched(f'summary="{summary}"', existing_issues)

    def get_or_create_issue_by_summary(self, summary: str, *args, **kw):
        found = self.get_issue_by_summary(summary)
        if found:
            return found

        return self.create_issue(summary, *args, **kw)

    def delete_issue(
        self, issue: JiraIssue, cascade: bool = False
    ) -> JiraIssue:
        if not issue.key:
            raise JiraClientException(f"issue does not have key: {issue}")

        message = f"deleting issue: {issue}"
        logger.debug(message)
        url = self.api_url(f"/issue/{issue.key}")
        response = self.http.delete(
            url, params={"deleteSubtasks": cascade and "true" or "false"}
        )
        data = self.validated_response(
            url, response, message
        )
        return data
