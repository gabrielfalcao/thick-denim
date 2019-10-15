# import pendulum
# from typing import List
# from humanfriendly.text import pluralize
from thick_denim.config import ThickDenimConfig

# from thick_denim.base import store_models, load_models
from thick_denim.networking.jira.client import JiraClient

# from thick_denim.networking.jira.models import JiraIssue


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")

    issue = client.get_issue("NA-38025")

    print(issue)
    print(issue.status_name)
    import ipdb

    ipdb.set_trace()
