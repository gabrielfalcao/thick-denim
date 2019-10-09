# -*- coding: utf-8 -*-

import os
import codecs
import functools
import pendulum
from thick_denim.base import Model as BaseModel


def datetime(func):
    @functools.wraps(func)
    def decorate(*args, **kw):
        val = func(*args, **kw)
        try:
            return pendulum.parse(val)
        except Exception:
            return val

    return decorate


class Model(BaseModel):
    __visible_atttributes__ = [
        "id",
        "html_url",
        "type",
        "sha",
        "created_at",
        "updated_at",
    ]

    @property
    def id(self):
        return self.get("id")

    @property
    def links(self):
        return self.get("_links")

    @property
    def url(self):
        return self.get("url")

    @property
    def html_url(self):
        return self.get("html_url")

    @property
    def type(self):
        return self.get("type", "")

    @property
    def sha(self):
        return self.get("sha", "")

    @property
    @datetime
    def created_at(self):
        return self.get("created_at")

    @property
    @datetime
    def updated_at(self):
        return self.get("updated_at")


class GithubTree(Model):
    __github_type__ = "tree"

    __visible_atttributes__ = ["sha", "path"]


class GithubUser(Model):
    __github_type__ = "user"

    __visible_atttributes__ = [
        "id",
        "login",
        "avatar_url",
        "site_admin",
        "html_url",
    ]

    @property
    def login(self):
        return self.get("login")

    @property
    def avatar_url(self):
        return self.get("avatar_url")

    @property
    def site_admin(self):
        return self.get("site_admin")


class GithubBlob(Model):
    __github_type__ = "blob"

    __visible_atttributes__ = ["sha", "path"]

    @property
    def encoding(self):
        return self.get("encoding")

    @property
    def content(self):
        return bytes(self.get("content"), "ascii")

    @property
    def bytes(self):
        return codecs.decode(self.content, self.encoding)

    @property
    def mode(self):
        return self.get("mode") or ""

    @property
    def filemode(self):
        code = self.mode[-3:]
        return int(code, 8)

    @property
    def path(self):
        return self.get("path") or ""

    @property
    def filename(self):
        return os.path.split(self.path)[-1]


class GithubIssue(Model):
    __github_type__ = "issue"

    __visible_atttributes__ = [
        "title",
        "number",
        "html_url",
        "assignee",
        "state",
    ]

    @property
    def title(self):
        return self.get("title")

    @property
    def number(self):
        return self.get("number")

    @property
    def state(self):
        return self.get("state")

    @property
    def assignee(self):
        return self.get("assignee")

    @property
    def body(self):
        return self.get("body")

    @property
    def labels(self):
        return self.get("labels")

    @property
    @datetime
    def closed_at(self):
        return self.get("closed_at")

    @property
    @datetime
    def merged_at(self):
        return self.get("merged_at")


class GithubPullRequest(GithubIssue):
    __github_type__ = "pull_request"


class GithubPullRequestComment(Model):
    __github_type__ = "pull_request_comment"

    __visible_atttributes__ = ["created_at", "author_name", "id"]

    @property
    def body(self):
        return self.get("body")

    @property
    def diff_hunk(self):
        return self.get("diff_hunk")

    @property
    def original_commit_id(self):
        return self.get("original_commit_id")

    @property
    def commit_id(self):
        return self.get("commit_id")

    @property
    def pull_request_url(self):
        return self.get("pull_request_url")

    @property
    def author_association(self):
        return self.get("author_association")

    @property
    def user(self):
        return GithubUser(self.get("user"))

    @property
    def author_name(self):
        return self.user.login
