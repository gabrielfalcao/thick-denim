from thick_denim.config import ThickDenimConfig
from thick_denim.networking.jira.client import JiraClient
from thick_denim.networking.jira.models import JiraIssue

mapping_ = {
    'To Do': 'To Do'
}


def main(config: ThickDenimConfig, args):
    client = JiraClient(config, "goodscloud")
    if len(args) != 1:
        print(f"USAGE: thick-denim run {__file__} ISSUE-01234")
        raise SystemExit(1)

    key = args[0]
    issue = client.get_issue(key)
    print(issue.format_robust_table())
    transition_issue_to_status_of_tdx_equivalent(client, issue)


def next_status(name):
    mapping = {
        'Backlog': 'To Do',
        'To Do': 'In Preparation',
        'In Progress': 'Ensure DoD',
        'Ensure DoD': 'Merged',
        'Merged': 'Done',
    }
    return mapping.get(name, name)


def translate_status_from_tdx(name):
    mapping = {
        'To Do': 'Backlog',
        'Ready ': 'To Do',
        'In Progress': 'In Progress',
        'Done': 'Done',
    }
    return mapping.get(name, name)


def transition_issue_to_status_of_tdx_equivalent(client: JiraClient, issue: JiraIssue):
    transitions = client.get_issue_transitions(issue)
    for clone_link in issue.issue_links.filter_by('type_name', 'Cloners'):
        original = client.get_issue(clone_link.source.key)
        if not original.key.startswith('TDX-'):
            print(f'skipping issue that does not originate from TDX: {original.key}')
            continue

        candidate_transitions =  transitions.filter_by(
            'name',
            translate_status_from_tdx(original.status_name),
        )
        candidate_transitions.extend(transitions.filter_by(
            'name',
            next_status(translate_status_from_tdx(original.status_name)),
        ))
        if not candidate_transitions:
            print(f'no matching transitions were found for {issue.key} whose original issue {original.key} was {original.status_name}')
            continue
        target = candidate_transitions[0]
        updated = client.transition_issue(issue, to=target)
        print(f'transitioned {issue.key} from {issue.status_name} to {updated.status_name}')
