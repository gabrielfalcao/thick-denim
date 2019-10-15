# -*- coding: utf-8 -*-
import pendulum
from thick_denim.base import Model


class JiraIssue(Model):
    __id_attributes__ = ["id"]
    __visible_atttributes__ = [
        "key",
        "issue_type_name",
        "summary",
        "assignee_key",
        "priority_name",
        "status_name",
    ]

    @property
    def id(self):
        return self.get("id")

    @property
    def key(self):
        return self.get("key")

    @property
    def parent(self):
        return self.get("Parent Link") or self.fields.get("parentLink")

    @property
    def created_at(self):
        value = self.fields.get("created") or self.get("Created")
        if value:
            return pendulum.parse(value)

    @property
    def updated_at(self):
        value = self.fields.get("updated") or self.get("Updated")
        if value:
            return pendulum.parse(value)

    @property
    def fields(self):
        return self.get("fields") or self.__data__

    @property
    def assignee(self):
        return self.fields.get("assignee") or self.get("Assignee") or {}

    @property
    def assignee_id(self):
        return self.assignee.get("id")

    @property
    def summary(self):
        return self.fields.get("summary") or self.get("Summary")

    @property
    def assignee_name(self):
        return self.assignee.get("displayName")

    @property
    def issue_type(self):
        return self.get("Issue Type") or {}

    @property
    def issue_type_name(self):
        return self.issue_type.get("name") or ""

    @property
    def priority(self):
        return self.get("Priority") or {}

    @property
    def priority_name(self):
        return self.priority.get("name") or ""

    @property
    def status(self):
        return self.get("Status") or {}

    @property
    def status_name(self):
        return self.status.get("name") or ""

    @property
    def assignee_key(self):
        return self.assignee.get("key")

    def with_updated_field_names(self, names):
        for code_name, humanized_name in names.items():
            value = self.fields.get(code_name, None)
            self[humanized_name] = value

        return self


class JiraProject(Model):
    __visible_atttributes__ = ["id", "key", "name", "style", "type_key"]
    __id_attributes__ = ["id"]

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
    __visible_atttributes__ = [
        "summary",
        "assignee_name",
        "assignee_key",
        "key",
    ]
    __id_attributes__ = ["id"]

    @property
    def id(self):
        return self.get("id")

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


class JiraIssueType(Model):
    __visible_atttributes__ = ["name", "id"]
    __id_attributes__ = ["id", "name"]

    @property
    def id(self):
        return self.get("id")

    @property
    def name(self):
        return self.get("name")

    @property
    def description(self):
        return self.get("description")

    @property
    def subtask(self):
        return self.get("subtask")

    @property
    def scope(self):
        return self.get("scope") or {}

    @property
    def scope_type(self):
        return self.scope.get("type")

    @property
    def project(self):
        return self.scope.get("project") or {}

    @property
    def project_id(self):
        return self.project.get("id")
