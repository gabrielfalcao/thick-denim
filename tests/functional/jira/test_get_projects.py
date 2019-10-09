from thick_denim.networking.jira.client import JiraClient
from thick_denim.networking.jira.models import (
    JiraProject,
    # JiraIssue,
)
from tests.harnesses import stub_config_with_jira_account
from tests.functional.harnesses import vcr_for_domain
# from tests.functional.harnesses import dump_json


vcr = vcr_for_domain("jira", record_mode="new_episodes")


def stubbed_jira_client():
    config = stub_config_with_jira_account(
        account_name="goodscloud",
        token="PLEASE USE A REAL TOKEN HERE",  # get one at https://id.atlassian.com/manage/api-tokens
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

    nextgen_projects = projects.filter_by("style", "next-gen")
    matrix = [
        (p.name, p.key) for p in nextgen_projects if isinstance(p, JiraProject)
    ]

    matrix.should.equal(
        [
            ("internal-finance-reporting", "IFR"),
            ("Incidents", "INC"),
            ("Incidents 1", "INC1"),
            ("NewStore Platform", "NP"),
            ("Poseidon DJ", "POS"),
            ("Poseidon", "PSD"),
            ("Poseidon Spring", "PSDN"),
            ("PythonSharedLibs", "PYT"),
            ("Scrum Masters", "SCRUM"),
            ("Security Incidents", "SEC"),
            ("Developer Experience", "TDX"),
        ]
    )


@vcr.use_cassette
def test_jira_get_issues():
    "retrieving issues from jira project"

    # Given a client
    client = stubbed_jira_client()

    # When I call get_projects()
    projects = client.get_projects(max_pages=-1)

    # Then I filter_by TDX
    candidates = projects.filter_by('key', 'TDX')
    candidates.should.have.length_of(1)
    devx = candidates[0]

    # When I list all issues from TDX
    issues = client.get_issues_from_project(devx.id)
    by_gabriel = issues.filter_by('assignee_key', '*gfalcao*')
    by_gabriel.should.have.length_of(60)

    closed_issues = by_gabriel.filter_by('key', 'TDX-78')

    # TODO: get changelogs
    # https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-issue-issueIdOrKey-changelog-get
    import ipdb;ipdb.set_trace()
