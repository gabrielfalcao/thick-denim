# -*- coding: utf-8 -*-
"""
contains utilities to make calls to the Github API
"""
import re
import logging
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlsplit, urlunsplit

from thick_denim.config import ThickDenimConfig
from thick_denim.ui import UserFriendlyObject
from .models import GithubPullRequest, GithubPullRequestComment, GithubBlob
from thick_denim.errors import ThickDenimError
from thick_denim.logs import UIReporter


ui = UIReporter("GitHub Client")

RESTFUL_LINKS_HEADER_REGEX = re.compile(
    r'[<](?P<url>[^>]+)[>][;]\s*rel="(?P<rel>\w+)"'
)


class GithubClientException(ThickDenimError):
    """raised when Github API returns a non 2xx response"""

    def __init__(self, url, data, status, message):
        message = f'{message}.\n{status} for url {url}: {data["message"]}'
        super().__init__(message)


def extract_query_string(url: str) -> dict:
    parsed = urlparse(url)
    params = {}
    for key, values in parse_qs(parsed.query).items():
        params[key] = values[0]

    return params


def regex_parse_link_part(part: str) -> dict:
    found = RESTFUL_LINKS_HEADER_REGEX.search(part)
    if found:
        return found.groupdict()

    return {}


class GithubClient(UserFriendlyObject):
    """client to the github api that uses the personal token from thick_denim config.
    """

    def __init__(
        self, config: ThickDenimConfig, repository_name: str, owner_name: str
    ):
        self.owner_name = owner_name
        self.repository_name = repository_name
        self.github_token = config.get_github_token()
        self.http = requests.Session()
        self.http.headers.update(
            {"Authorization": f"token {self.github_token}"}
        )

    def validated_response(self, url, response, message):
        status = response.status_code
        data = response.json()
        if status in (200, 201):
            return data

        full_name = f"{self.owner_name}/{self.repository_name}"
        raise GithubClientException(
            url, data, status, "{message} ({full_name})"
        )

    def api_url(self, path: str):
        full_name = f"{self.owner_name}/{self.repository_name}"
        return f'https://api.github.com/repos/{full_name}/{path.lstrip("/")}'

    def download_blob(self, sha: str) -> requests.Response:
        url = self.api_url(f"/git/blobs/{sha}")
        data = self.validated_response(
            url, self.http.get(url), f"downloading blob {sha}"
        )
        return data

    def get_tree(self, tree_sha: str = "HEAD", recursive: bool = False):
        url = self.api_url(f"/git/trees/{tree_sha}?recursive={int(recursive)}")
        return self.validated_response(
            url, self.http.get(url), f"retrieving git tree for {tree_sha}"
        )

    def get_refs(self, name: str = "master", reftype: str = "heads"):
        url = self.api_url(f"/git/refs/{reftype}/{name}")
        return self.validated_response(
            url,
            self.http.get(url),
            f"retrieving git refs for {reftype}/{name}",
        )

    def walk_tree(self, path: str, sha: str):
        ui.debug(
            f"recursively walking tree {sha} for path starting with {path!r}"
        )
        root = self.get_tree(sha, recursive=True)
        nodes = root["tree"]

        for node in nodes:
            if node["path"].startswith(path):
                yield node

    def list_blobs(self, path: str, branch: str = "master"):
        root_ref = self.get_refs(branch)
        sha = root_ref["object"]["sha"]

        ui.report(f"listing blobs in {path} from branch {branch} ({sha})")
        for node in self.walk_tree(path, sha):
            if node["type"] == "blob":
                node.update(self.download_blob(node["sha"]))
                yield GithubBlob(node)

    def extract_restful_links(self, response):
        link = response.headers.get("Link")
        if not link:
            return {}

        links = {}
        for item in filter(bool, map(regex_parse_link_part, link.split(","))):
            links.update({item["rel"]: item["url"]})

        return links

    def get_next_restful_url(self, response, params: dict):
        routes = self.extract_restful_links(response)
        link = routes.get("next") or {}
        if not link:
            return

        link_params = extract_query_string(link)
        params.update(link_params)
        scheme, location, path, query, fragment = urlsplit(link)
        query = urlencode(params)
        return urlunsplit((scheme, location, path, query, fragment))

    def request_with_pages(
        self, url, message: str, max_pages: int, params: dict = {}
    ):
        response = self.http.get(self.api_url(url), params=params)
        next_url = self.get_next_restful_url(response, params)

        current_page = 1
        items = self.validated_response(url, response, message)
        ui.debug(message)
        should_request_next_page = (
            lambda: max_pages < 0 or current_page <= max_pages
        )
        while next_url and should_request_next_page():
            ui.debug(f"next page: {next_url}")
            current_page += 1
            response = self.http.get(next_url)
            next_url = self.get_next_restful_url(response, params)
            msg = f"{message} (page {current_page})"
            items.extend(self.validated_response(next_url, response, msg))
            ui.debug(msg)

        return items

    def list_pull_requests(self, state="open", max_pages: int = 0):
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # states: open, closed, all
        params = {"state": state, "sort": "updated"}
        result = self.request_with_pages(
            url="/pulls",
            params=params,
            message="retrieving pull-requests",
            max_pages=max_pages,
        )
        return GithubPullRequest.List(result)

    def list_comments_from_pull_request(
        self, pull_request_number, max_pages: int = 0
    ):
        # https://developer.github.com/v3/pulls/comments/#list-comments-on-a-pull-request
        params = {
            "sort": "created",
            "direction": "asc",
            # 'since': 'YYYY-MM-DDTHH:MM:SSZ',  # ISO-8601 format
        }
        result = self.request_with_pages(
            url=f"/pulls/{pull_request_number}/comments",
            params=params,
            message="retrieving comments from pull-request #{pull_request_number}",
            max_pages=max_pages,
        )
        return GithubPullRequestComment.List(result)
