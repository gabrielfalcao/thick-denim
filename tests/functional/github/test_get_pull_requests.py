from thick_denim.networking.github import GithubClient
from tests.harnesses import stub_config_with_github_token
from tests.functional.harnesses import vcr_for_domain

# from tests.functional.harnesses import dump_json


vcr = vcr_for_domain("github", record_mode="new_episodes")


def stubbed_github_client(repository_name):
    config = stub_config_with_github_token(
        token="REDACTED - please use yours"  # get one here https://github.com/settings/tokens
    )
    client = GithubClient(config, repository_name, owner_name="NewStore")
    return client


@vcr.use_cassette
def test_github_get_pull_requests():
    "retrieving pull requests from github repository"

    # Given a client
    client = stubbed_github_client(repository_name="newstore")

    # When I  get all pull-requests
    all_pull_requests = client.list_pull_requests("open", max_pages=-1)

    # Then it should have returned issues
    all_pull_requests.should.have.length_of(90)


@vcr.use_cassette
def test_github_get_comments_from_pr():
    "retrieving pull requests from github repository"

    # Given a client
    client = stubbed_github_client(repository_name="newstore")

    # When I  get the open pull requests
    open_prs = client.list_pull_requests("open", max_pages=-1)

    # Then it should have returned pull requests
    open_prs.should.have.length_of(111)

    # When I get the issues from the first PR
    buildbot_prs = open_prs.filter_by("title", "*postgres*from*run-infra*")
    buildbot_prs.should.have.length_of(1)
    database2_buildbot_pr = buildbot_prs[0]
    comments_on_buildbot_pr = client.list_comments_from_pull_request(
        database2_buildbot_pr.number, max_pages=-1
    )
    comments_on_buildbot_pr.should.have.length_of(6)

    comments = [
        (comment.author_name, comment.body)
        for comment in comments_on_buildbot_pr
    ]

    comments.should.have.equal(
        [
            (
                "bjjb",
                "Why not blow up here? Am I missing something? Surely if the binary's missing, there's no point continuing.",
            ),
            (
                "gabrielfalcao",
                "The binary check is part of what determines if embedded postgres should be used or not.\r\nThat is to say, `database2` will still point to a single postgres instance in case `NEWSTORE_RUNTIME_NO_CONSUL=true` is set but the postgres binaries are unavailable.",
            ),
            ("bjjb", "WTF?"),
            ("gabrielfalcao", "Yeah, not sure how this is passing on master."),
            (
                "gabrielfalcao",
                "last relevant commit on `logistic_order_service` seems to pre-date the migration to postgres 10. Perhaps the date string from postgres changed to ISO-8601 and caused this test to fail",
            ),
            (
                "gabrielfalcao",
                "I suspect that we might have more success reducing the concurrency, rather than increasing",
            ),
        ]
    )
