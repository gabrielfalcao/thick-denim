from pathlib import Path
from .util import guess_config_path

from thick_denim.models import DataBag
from thick_denim.fs import load_yaml_data_from_path
from .errors import NoConfigFound


class ThickDenimConfig(DataBag):
    """Configuration utility with the following features:

     - parse config file from ~/.newstore.yml
     - generate authentication data for AWS
    """

    def __init__(self, path: Path = None, data=None):
        self.path = path or (data or guess_config_path()) or None
        data = data or load_yaml_data_from_path(self.path)
        super().__init__(data)

    def get_jira_key(self, account_name: str, key: str) -> str:
        value = self.traverse("jira", "accounts", account_name, key)
        if not value:
            raise NoConfigFound(f'config key "jira.{key}" is missing')
        return value

    def get_jira_server(self, account_name: str):
        return self.get_jira_key(account_name, "server")

    def get_jira_email(self, account_name: str):
        return self.get_jira_key(account_name, "email")

    def get_jira_personal_token(self, account_name: str):
        return self.get_jira_key(account_name, "token")

    def get_github_token(self):
        return self.traverse("github", "token")
