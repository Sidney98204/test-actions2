import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os
import argparse

parser = argparse.ArgumentParser()
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

pr_url = f"https://github.com/Sidney98204/test-actions2/pull/{pr_number}"
issue_title = f"Review dependencies pull request: {pr_title}"
issue_description = f"{pr_url}\n{pr_title}"

if len(reviewers) == 0:
    raise Exception("No reviewers were assigned")

reviewer = reviewers[0]["login"]
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

r = response.json()
issues = r["data"]["team"]["issues"]["nodes"]
for issue in issues:
  print(issue)
  issue_description = issue["description"]
  if issue_description and pr_url in issue_description:
    print("DUPLICATE ISSUE, NOT CREATING A NEW ONE")
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
    print(response.json())
    # grab issue id
    issue_id = response.json()["data"]["issueCreate"]["issue"]["id"]
    print(issue_id)
    
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
            title: "I AM THE UPDATED PULL REQUEST"
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
        print(response.text)
    else:
        print("No Todo state found, not transitioning issue")