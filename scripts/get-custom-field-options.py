import json
from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    if len(args) != 1:
        print(f"USAGE: thick-denim run {__file__} 10009  # or any field id")
        raise SystemExit(1)

    key = args[0]
    options = client.get_custom_field_options('10009')
    print(json.dumps(options))
    import ipdb;ipdb.set_trace()
