from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    project = client.get_project("TDX")
    properties = client.get_project_properties(project)
    print(project.format_pretty_table())
    print('\nproperties:\n')
    for key in properties.keys:
        print(f'\t{key}')
