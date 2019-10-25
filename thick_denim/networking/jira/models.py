# -*- coding: utf-8 -*-
import re
import pendulum
from thick_denim.base import Model, extract_json_from_field


class JiraIssue(Model):
    __id_attributes__ = ["id"]
    __visible_atttributes__ = [
        "key",
        "issue_type_name",
        "summary",
        "assignee_key",
        "priority_name",
        "status_name",
        "created",
        "updated",
        "url",
    ]

    @property
    def id(self):
        return self.get("id")

    @property
    def key(self):
        return self.get("key") or self.extract_key_from_watchers_link() or ""

    def extract_key_from_watchers_link(self):
        # workaround for classic projects whose response does not
        # include the issue key
        found = re.search(
            r"/issue/(?P<key>[A-Z][A-Z0-9]+[-]\d+)/watchers",
            self.watchers_link,
        )
        if found:
            return found.group("key")

    @property
    def watches(self):
        return self.fields.get("watches") or {}

    @property
    def epic_link(self):
        return self.fields.get("Epic Link") or self.fields.get(
            "customfield_10009"
        )

    @property
    def url(self):
        return f"{self.base_url}/browse/{self.key}"

    @property
    def base_url(self):
        found = re.search(
            r"^(?P<base_url>https?:[/][/].*atlassian.net/).*",
            self.watchers_link,
        )
        if not found:
            return ""

        return found.group("base_url")

    @property
    def watchers_link(self):
        return self.watches.get("self") or ""

    @property
    def parent(self):
        value = self.get("parent") or self.fields.get("parent")
        if value:
            return JiraIssue(value)

    @property
    def issue_links(self):
        values = self.fields.get("issuelinks") or []
        return JiraIssueLink.List(values)

    @property
    def project(self):
        value = self.get("project") or self.fields.get("project")
        if value:
            return JiraProject(value)

    @property
    def description(self):
        return self.fields.get("description")

    @property
    def created_at(self):
        value = self.fields.get("created") or self.get("Created")
        if value:
            return pendulum.parse(value)

    @property
    def created_day(self):
        return self.created_at.format("DD/MM/YYYY HH:MM:SS")

    @property
    def created_ago(self):
        return self.created_at and self.created_at.diff_for_humans()

    @property
    def created(self):
        return f"{self.created_ago} ({self.created_day})"

    @property
    def updated_at(self):
        value = self.fields.get("updated") or self.get("Updated")
        if value:
            return pendulum.parse(value)

    @property
    def updated_day(self):
        return self.updated_at.format("DD/MM/YYYY HH:MM:SS")

    @property
    def updated_ago(self):
        return self.updated_at and self.updated_at.diff_for_humans()

    @property
    def updated(self):
        return f"{self.updated_ago} ({self.updated_day})"

    @property
    def fields(self):
        return self.get("fields") or self.__data__

    @property
    def assignee(self):
        return self.fields.get("assignee") or self.get("Assignee") or {}

    @property
    def reporter(self):
        return self.fields.get("reporter") or self.get("Reporter") or {}

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
        return JiraIssueType(self.get("Issue Type") or {})

    @property
    def issue_type_name(self):
        return self.issue_type.name

    @property
    def priority(self):
        return self.get("Priority") or {}

    @property
    def priority_name(self):
        return self.priority.get("name") or ""

    @property
    def status(self):
        return JiraIssueStatus(self.get("Status") or {})

    @property
    def status_name(self):
        return self.status.name

    @property
    def assignee_key(self):
        return self.assignee.get("key")

    @property
    def reporter_key(self):
        return self.reporter.get("key")

    def with_updated_field_names(self, names):
        for code_name, humanized_name in names.items():
            value = self.fields.get(code_name, None)
            self[humanized_name] = value

        return self

    @property
    def development(self):
        value = self.fields.get("customfield_12200")
        return extract_json_from_field(value)

    @property
    def devteam_meta(self):
        return self.fields.get("customfield_10602", {})

    @property
    def devteam(self):
        return self.devteam_meta.get("value")


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
        return JiraProject(self.scope.get("project") or {})

    @property
    def project_id(self):
        return self.project.id


class JiraIssueLinkType(Model):
    __visible_atttributes__ = ["name", "id"]
    __id_attributes__ = ["id", "name"]

    @property
    def id(self):
        return self.get("id")

    @property
    def name(self):
        return self.get("name")


class JiraIssueLink(Model):
    __visible_atttributes__ = ["name", "id", "source", "target"]
    __id_attributes__ = ["id", "name"]

    @property
    def type(self):
        return self.get("type") or {}

    @property
    def id(self):
        return self.get("id")

    @property
    def type_name(self):
        return self.type.get("name")

    @property
    def name(self):
        return self.get("name")

    @property
    def source(self):
        value = self.get("inwardIssue") or {}
        return JiraIssue(value)

    @property
    def target(self):
        value = self.get("outwardIssue") or {}
        return JiraIssue(value)


class JiraCustomField(Model):
    __visible_atttributes__ = ["name", "id"]
    __id_attributes__ = ["id", "key"]

    @property
    def id(self):
        return self.get("id")

    @property
    def key(self):
        return self.get("key")

    @property
    def name(self):
        return self.get("name")

    @property
    def description(self):
        return self.get("description")

    @property
    def scope(self):
        return self.get("scope") or {}

    @property
    def scope_type(self):
        return self.scope.get("type")

    @property
    def project(self):
        return JiraProject(self.scope.get("project") or {})

    @property
    def project_id(self):
        return self.project.id


class JiraIssueStatus(Model):
    __visible_atttributes__ = [
        "name",
        "id",
        "color",
        "category_key",
        "category_id",
    ]
    __id_attributes__ = ["id", "name"]

    @property
    def id(self):
        return self.get("id")

    @property
    def name(self):
        return self.get("name")

    @property
    def category_key(self):
        return self.category.get("key")

    @property
    def category_name(self):
        return self.category.get("name")

    @property
    def category_id(self):
        return self.category.get("id")

    @property
    def description(self):
        return self.get("description")

    @property
    def category(self):
        return self.get("statusCategory") or {}

    @property
    def color(self):
        return self.category.get("colorName")

    @property
    def scope(self):
        return self.get("scope") or {}

    @property
    def scope_type(self):
        return self.scope.get("type")

    @property
    def project(self):
        return JiraProject(self.scope.get("project") or {})

    @property
    def project_id(self):
        return self.project.id


class JiraProjectProperties(Model):
    __visible_atttributes__ = ["keys"]
    __id_attributes__ = ["keys"]

    @property
    def keys(self):
        return [i.get("key") for i in self.get("keys", [])]

    # def get_table_rows(self):
    #     return self.keys


class JiraIssueTransition(Model):
    __visible_atttributes__ = ["name", "id", "category_name", "category_key"]
    __id_attributes__ = ["id", "name"]

    @property
    def id(self):
        return self.get("id")

    @property
    def fields(self):
        return self.get("fields") or {}

    @property
    def to(self):
        return JiraIssueStatus(self.get("to") or {})

    @property
    def name(self):
        return self.to.name

    @property
    def category_key(self):
        return self.to.category_key

    @property
    def category(self):
        return self.to.category

    @property
    def category_name(self):
        return self.to.category_name
