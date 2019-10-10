# -*- coding: utf-8 -*-

from thick_denim.base import Model


class JiraIssue(Model):
    __visible_atttributes__ = ["summary", "assignee_name", "assignee_key", "key"]

    @property
    def key(self):
        return self.get("key")

    @property
    def fields(self):
        return self.get("fields") or {}

    @property
    def assignee(self):
        return self.fields.get("assignee") or {}

    @property
    def summary(self):
        return self.fields.get("summary")

    @property
    def assignee_name(self):
        return self.assignee.get("displayName")

    @property
    def assignee_key(self):
        return self.assignee.get("key")


class JiraProject(Model):
    __visible_atttributes__ = ["id", "key", "name", "style", "type_key"]

    @property
    def name(self):
        return self.get("name")

    @property
    def id(self):
        return self.get("id")

    @property
    def uuid(self):
        return self.get("uuid")

    @property
    def type_key(self):
        return self.get("projectTypeKey")

    @property
    def style(self):
        return self.get("style")

    @property
    def key(self):
        return self.get("key")


class JiraIssueChangelog(Model):
    __visible_atttributes__ = ["summary", "assignee_name", "assignee_key", "key"]

    @property
    def author(self):
        return self.get("author") or {}

    @property
    def author_name(self):
        return self.author.get("name")

    @property
    def created_at(self):
        return self.get("created")

    @property
    def items(self):
        return self.get("items")
