# -*- coding: utf-8 -*-
"""
contains utilities to make calls to the Jira API
"""

import requests
import logging
from thick_denim.errors import ThickDenimError
from thick_denim.config import ThickDenimConfig
from thick_denim.logs import UIReporter
from .models import JiraIssue, JiraProject


ui = UIReporter("Jira Client")


logger = logging.getLogger(__name__)


class JiraClientException(ThickDenimError):
    """raised when Jira API returns a non 2xx response"""

    def __init__(self, url, data, status, message):
        message = f'{message}.\n{status} for url {url}: {data}'
        super().__init__(message)


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
        self.http.headers.update({
            "Bearer": f"{self.jira_token}",
            "Accept": "application/json",
            # "Content-Type": "application/json",
        })

    def api_url(self, path: str):
        return f'{self.jira_server}/rest/api/3/{path.lstrip("/")}'

    def get_issue(self, issue_key):
        logger.debug(f"retrieving issue {issue_key}")
        response = self.http.get(self.api_url(f"/issue/{issue_key}")).json()
        data = response["fields"]
        return JiraIssue(data)

    def get_issues_from_project(self, id_or_key, max_pages: int = -1):
        # https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-search-post
        start = 0
        params = {
            "expand": ["names", "schema", "operations"],
            "jql": f"project = {id_or_key}",
            "maxResults": 100,
            "fieldsByKeys": False,
            "fields": "*all",
            "startAt": start,
        }
        current_page = 1
        logger.debug(f"retrieving issues from project {id_or_key}")
        url = self.api_url(f"/search")
        response = self.http.get(url, params=params)
        data = self.validated_response(url, response, f'retrieving issues for project {id_or_key}')
        total = data['total']
        items = data['issues']
        should_request_next_page = (
            lambda: max_pages < 0 or current_page <= max_pages
        )

        while len(items) < total and should_request_next_page():
            current_page += 1
            params['startAt'] = len(items)
            response = self.http.get(url, params=params)
            data = self.validated_response(url, response, f'retrieving issues for project {id_or_key} (page {current_page})')
            total = data['total']
            items.extend(data['issues'])

        return JiraIssue.List(items)

    def request_with_pages(
        self, url, message: str, max_pages: int, params: dict = {}
    ):
        current_page = 1
        ui.debug(message)
        response = self.http.get(self.api_url(url))
        data = self.validated_response(url, response, message)
        next_url = data.get("nextPage")
        items = data["values"]

        should_request_next_page = (
            lambda: max_pages < 0 or current_page <= max_pages
        )
        while next_url and should_request_next_page():
            ui.debug(f"next page: {next_url}")
            current_page += 1
            msg = f"{message} (page {current_page})"
            response = self.http.get(next_url)
            data = self.validated_response(next_url, response, msg)
            next_url = data.get("nextPage")
            items.extend(data["values"])
            ui.debug(msg)

        return items

    def get_projects(self, max_pages: int = 1):
        logger.debug(f"retrieving all projects")
        params = {"maxResults": 50, "startAt": 0, "orderBy": "key"}

        items = self.request_with_pages(
            "/project/search",
            "retrieving projects",
            max_pages=max_pages,
            params=params,
        )
        return JiraProject.List(items)

    def get_project(self, id_or_key):
        logger.debug(f"retrieving project {id_or_key}")
        data = self.http.get(self.api_url(f"/project/{id_or_key}")).json()
        return JiraProject(data)

    def validated_response(self, url, response, message):
        status = response.status_code

        if status in (200, 201):
            data = response.json()
            return data
        else:
            data = response.text

        raise JiraClientException(url, data, status, message)
