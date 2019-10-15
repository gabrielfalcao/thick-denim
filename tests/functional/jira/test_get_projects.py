from thick_denim.networking.jira.client import JiraClient

# from thick_denim.networking.jira.models import (
#     JiraProject,
#     JiraIssue,
# )
from tests.harnesses import stub_config_with_jira_account
from tests.functional.harnesses import vcr_for_domain
from tests.functional.harnesses import dump_json


vcr = vcr_for_domain("jira", record_mode="new_episodes")


def stubbed_jira_client():
    config = stub_config_with_jira_account(
        account_name="goodscloud",
        token="TkgAvPMm6GXXFn2Ulr3VD28C",  # get one at https://id.atlassian.com/manage/api-tokens
        email="gfalcao@newstore.com",
    )
    client = JiraClient(config, "goodscloud")
    return client


@vcr.use_cassette
def test_jira_get_projects():
    "retrieving jira projects"

    # Given a client
    client = stubbed_jira_client()

    # When I call get_projects()
    projects = client.get_projects(max_pages=-1)

    # Then I should get a list with all current projects
    projects.should.have.length_of(55)

    # And I dump the projects to json
    dump_json("jira.projects.json", projects.to_dict())
    # classic_projects = projects.filter_by("style", "classic")
    # nextgen_projects = projects.filter_by("style", "next-gen")

    # matrix = [
    #     (p.name, p.key) for p in nextgen_projects if isinstance(p, JiraProject)
    # ]

    # matrix.should.equal(
    #     [
    #         ("internal-finance-reporting", "IFR"),
    #         ("Incidents", "INC"),
    #         ("Incidents 1", "INC1"),
    #         ("NewStore Platform", "NP"),
    #         ("Poseidon DJ", "POS"),
    #         ("Poseidon", "PSD"),
    #         ("Poseidon Spring", "PSDN"),
    #         ("PythonSharedLibs", "PYT"),
    #         ("Scrum Masters", "SCRUM"),
    #         ("Security Incidents", "SEC"),
    #         ("Developer Experience", "TDX"),
    #     ]
    # )


@vcr.use_cassette
def test_jira_get_issues_from_newstore_apps():
    "retrieving issues from jira project"

    # Given a client
    client = stubbed_jira_client()

    # # When I call get_projects()
    # projects = client.get_projects(max_pages=-1)

    # # Then I filter_by TDX
    # candidates = projects.filter_by('key', 'NA')
    # candidates.should.have.length_of(1)
    # newstore_apps = candidates[0]

    # When I list all issues from NEWSTORE APPS
    issues_NA = client.get_issues_from_project("NA", max_pages=2)
    # And I list all issues from DEVX
    issues_TDX = client.get_issues_from_project("TDX", max_pages=2)

    # Then I dump them to json
    dump_json("jira.issues.NA.json", issues_NA.to_dict())
    dump_json("jira.issues.TDX.json", issues_TDX.to_dict())


@vcr.use_cassette
def test_get_changelogs_from_issues():
    "retrieving change logs from an issue"

    # Given a client
    client = stubbed_jira_client()

    # When I list all changelogs from an issue of classic project
    changes_classic = client.get_changelogs_from_issue("NA-38201", max_pages=1)

    # And I list all changelogs from an issue of next-gen project
    changes_next_gen = client.get_changelogs_from_issue("TDX-165", max_pages=1)

    # Then I dump the data
    dump_json("jira.issue.NA-38201.changelog.json", changes_classic.to_dict())
    dump_json("jira.issue.TDX-165.changelog.json", changes_next_gen.to_dict())
