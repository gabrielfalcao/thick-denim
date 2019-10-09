# -*- coding: utf-8 -*-

from newstore.runtime import test_mode
from newstore import logs

if not test_mode():
    import inquirer
else:
    inquirer = None


SUPPORTED_AWS_PROFILES = [
    "remote-development",
    "develop",
    "sandbox",
    "staging",
    "prod",
]


class ConsoleApplication(object):
    __sections__ = {}

    def __init__(self, config: "newstore.config.NewStoreConfig"):
        self.config = config
        self.sections = {}
        self.state = {}
        for name, cls in self.__sections__.items():
            self.sections[name] = cls(name, self)

    def run_section(self, name, *args, **kw):
        section = self.get_section(name)
        section.run(*args, **kw)

    def get_section(self, name):
        return self.sections.get(name)

    def run_all(self):
        for name in self.sections.keys():
            self.run_section(name)


class DataSection(object):
    def __init__(self, name: str, parent: ConsoleApplication):
        self.name = name
        self.application = parent
        self.config = parent.config
        self.state = {}

    def run(self, *args, **kw):
        return self.process_result(self.prompt(*args, **kw))

    def prompt(self, *args, **kw):
        return inquirer.prompt(self.questions(*args, **kw))

    def process_result(self, data: dict):
        if not data:
            print(f"Operation canceled")
            return

        self.state.update(data or {})
        self.config.update(self.state)

        try:
            self.config.write()
            logs.print(f"\033[1;32mSaved: {self.config.path}\033[0m")
        except Exception as e:
            logs.print_err(str(e))
            raise SystemExit(1)

    def questions(self, *args, **kw):
        return []


class AWSDataSection(DataSection):
    @property
    def profile_name(self):
        return self.state.get("profile_name")

    def process_result(self, data: dict):
        if not data:
            print(f"Operation canceled")
            return

        self.state.update(data or {})
        self.config.traverse("aws", "profiles", self.profile_name).update(
            self.state
        )

        self.state.pop("profile_name", None)  # remove redundant field
        # prior to writing

        try:
            self.config.write()
            logs.print(f"\033[1;32mSaved: {self.config.path}\033[0m")
        except Exception as e:
            logs.print_err(str(e))
            raise SystemExit(1)

    def run(self, profile_name: str = None, *args, **kw):
        if not self.profile_name:
            self.inquire_profile(profile_name)

        return super().run(*args, **kw)

    def inquire_profile(self, profile_name: str):
        if self.profile_name:
            return

        if profile_name:
            self.state["profile_name"] = profile_name
            return

        self.state.update(
            inquirer.prompt(
                [
                    inquirer.List(
                        "profile_name",
                        message="Choose an AWS Profile to configure:",
                        choices=SUPPORTED_AWS_PROFILES,
                    )
                ]
            )
            or {}
        )

    def get_profile_config(self, key):
        return self.config.traverse("aws", "profiles", self.profile_name, key)

    def questions(self):
        if not self.profile_name:
            logs.print_err(f"You must select an AWS profile to proceed")
            raise SystemExit(1)

        questions = []
        KEYS = [
            "aws_access_key_id",
            "aws_secret_access_key",
            "username",
            "mfa_secret",
        ]
        for key in KEYS:
            value = self.get_profile_config(key)
            message = (
                value
                and f"Please ensure the value for {key!r} is correct:"
                or f"{key!r} cannot be empty, set one:"
            )
            questions.append(
                inquirer.Text(key, default=value, message=message)
            )

        questions.append(
            inquirer.Checkbox(
                "roles",
                message=f"Use 'spacebar' to mark the roles your user can assume in profile {self.profile_name}",
                default=self.get_profile_config("roles") or [],
                choices=[
                    "devops",
                    "eks-deployer",
                    "onDuty",
                    "integrator",
                    "IAM-Master",
                ],
            )
        )
        return questions


class BasicDataSection(DataSection):
    def questions(self):
        questions = []
        email = self.config.get("email")
        github_token = self.config.get("github_token")
        questions.append(
            inquirer.Text(
                "email",
                default=email,
                message=email
                and f"Please check if your email is correct:"
                or f"please type your @newstore.com email:",
            )
        )
        questions.append(
            inquirer.Text(
                "github_token",
                default=github_token,
                message=email
                and f"Please check if your personal github access token is correct:"
                or f"please create a new github access token and type it here:",
            )
        )

        return questions


class ConfigWizardApplication(ConsoleApplication):
    __sections__ = {"basic": BasicDataSection, "aws": AWSDataSection}
