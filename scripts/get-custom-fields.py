import json
from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    project = client.get_project("NA")
    options = client.get_custom_fields(project)

    import ipdb

    ipdb.set_trace()
