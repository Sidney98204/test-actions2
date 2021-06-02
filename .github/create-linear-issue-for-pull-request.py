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
issue_description = f"{pr_url}: {pr_title}"

if len(reviewers) == 0:
    raise Exception("No reviewers were assigned")

# TODO: Do we potentially wanna loop over the reviewers? 
reviewer = reviewers[0]["login"]
# TODO: point this to the right file
with open(".github/reviewers-linear-info-TEST.json") as file:
    reviewers_info = json.loads(file.read())
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
    # Create issue
    query = """mutation {{
    issueCreate(
        input: {{
        title: "Review dependencies pull request"
        description: "{issue_description}"
        teamId: "{team_id}"
        }}
    ) {{
        success
        issue {{
        id
        title
        }}
    }}
    }}""".format(issue_description=issue_description, team_id=project_key)
    response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
    print(f"CREATE ISSUE RESPONSE: {response.json()}")
    # grab issue id
    issue_id = response.json()["data"]["issueCreate"]["issue"]["id"]
    
    # get workflow states
    query = """query {
    workflowStates {
        nodes {
        id
        name
        }
    }
    }"""
    response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
    states = response.json()["data"]["workflowStates"]["nodes"]
    for state in states:
        if state["name"] == "Todo":
            state_id = state["id"]

    # Transition issue into To Do
    if state_id:
        query = """mutation {{
        issueUpdate(
            id: "{issue_id}",
            input: {{
            stateId: "{state_id}",
            }}
        ) {{
            success
            issue {{
            id
            title
            state {{
                id
                name
            }}
            }}
        }}
        }}""".format(issue_id=issue_id, state_id=state_id)
        response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
        print(f"TRANSITION ISSUE RESPONSE: {response.json()}")
    else:
        print("No Todo state found, not transitioning issue")