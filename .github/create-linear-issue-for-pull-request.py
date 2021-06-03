import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os
import argparse

parser = argparse.ArgumentParser()
# TODO: Tell Ilya to create a new secret for LINEAR API TOKEN
parser.add_argument("-p", "--password", required=True)
parser.add_argument("-e", "--event", required=True)

io_args = parser.parse_args()
LINEAR_API_TOKEN = io_args.password
event_path = io_args.event

if not os.path.isfile(event_path):
  raise Exception("Couldn't find github event file")

with open(event_path) as file:
  file_contents = file.read()
  event_obj = json.loads(file_contents)

reviewers = event_obj["pull_request"]["requested_reviewers"]
pr_title = event_obj["pull_request"]["title"]
pr_number = event_obj["pull_request"]["number"]

# TODO: Fix URL for front end repo
pr_url = f"https://github.com/Sidney98204/test-actions2/pull/{pr_number}"
issue_title = f"Review dependencies pull request: {pr_title}"
issue_description = f"{pr_title}: {pr_url}"

if len(reviewers) == 0:
    raise Exception("No reviewers were assigned")

with open(".github/reviewers-linear-info-TEST.json") as file:
    reviewers_info = json.loads(file.read())
for reviewer_info in reviewers:
    reviewer = reviewer_info["login"]
    # TODO: point this to the right file
    reviewer_info = reviewers_info[reviewer]
    project_key = reviewer_info["project_key"]
    reviewer_id = reviewer_info["linear_id"]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': LINEAR_API_TOKEN,
    }

    # Check existing issues to see if this issue has already been created
    query = """query {{
    team(id: "{team_id}") {{
        id
        name
        issues {{
        nodes {{
            id
            title
            description
            assignee {{
            id
            name
            }}
            createdAt
            archivedAt
        }}
        }}
    }}
    }}""".format(team_id=project_key)

    response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
    print(response.text)
    # TODO: remove print statement

    r = response.json()
    issues = r["data"]["team"]["issues"]["nodes"]
    issue_exists = False
    for issue in issues:
        if issue["description"] and pr_url in issue["description"]:
            issue_exists = True

    if issue_exists:
        print("Issue already exists")
    else: 
        # get workflow states
        query = """query {
        workflowStates {
            nodes {
            id
            name
            team {
                id
            }
            }
        }
        }"""
        response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
        states = response.json()["data"]["workflowStates"]["nodes"]
        # order of preference, the larger the better
        states_to_preference = {"Inbox": 2, "Accepted": 1, "Todo": 1, "To do": 1, "Backlog": 0, "": -1}
        state_name = ""
        state_id = ""
        for state in states:
            if (state["name"] in states_to_preference.keys() and 
                    state["team"]["id"] == project_key and 
                    states_to_preference.get(state["name"], -1) > states_to_preference[state_name]):
                state_id = state["id"]
                state_name = state["name"]


        # Create issue
        query = """mutation {{
        issueCreate(
            input: {{
            title: "Review dependencies pull request"
            description: "{issue_description}"
            teamId: "{team_id}"
            assigneeId: "{reviewer_id}"
            stateId: "{state_id}"
            }}
        ) {{
            success
            issue {{
            id
            title
            }}
        }}
        }}""".format(issue_description=issue_description, team_id=project_key, reviewer_id=reviewer_id, state_id=state_id)
        response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
        print(f"CREATE ISSUE RESPONSE: {response.json()}")
        # grab issue id
        issue_id = response.json()["data"]["issueCreate"]["issue"]["id"]
    

        # Transition issue into To Do
        # if state_id:
        #     query = """mutation {{
        #     issueUpdate(
        #         id: "{issue_id}",
        #         input: {{
        #         stateId: "{state_id}",
        #         }}
        #     ) {{
        #         success
        #         issue {{
        #         id
        #         title
        #         state {{
        #             id
        #             name
        #         }}
        #         }}
        #     }}
        #     }}""".format(issue_id=issue_id, state_id=state_id)
        #     response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
        #     print(f"TRANSITION ISSUE RESPONSE: {response.json()}")
        # else:
        #     print("No Todo state found, not transitioning issue")