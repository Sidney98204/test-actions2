import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os
import argparse

print(os.getcwd())
print(os.listdir())

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", required=True)
parser.add_argument("-p", "--password", required=True)
parser.add_argument("-e", "--event", required=True)

io_args = parser.parse_args()
JIRA_API_EMAIL = io_args.username
JIRA_API_TOKEN = io_args.password
event_path = io_args.event

print(f"{len(JIRA_API_EMAIL)} and {len(JIRA_API_TOKEN)}")
if not os.path.isfile(event_path):
  raise Exception("Couldn't find github event file")

with open(event_path) as file:
  file_contents = file.read()
  event_obj = json.loads(file_contents)

reviewers = event_obj["pull_request"]["requested_reviewers"]
pr_body = event_obj["pull_request"]["body"]
jira_id = reviewer_jira_info["jira_id"]

jira_description = f"https://github.com/Sidney98204/test-actions2/pull/{pr_number} \n {pr_body}"

if len(reviewers) == 0:
    raise Exception("No reviewers were assigned")

reviewer = reviewers[0]["login"]
with open("reviewers-jira-info.json") as file:
    reviewers_jira_info = json.loads(file.read())
reviewer_jira_info = reviewers_jira_info[reviewer]
project_key = reviewer_jira_info["project_key"]
jira_id = reviewer_jira_info["jira_id"]

auth = HTTPBasicAuth(JIRA_API_EMAIL, JIRA_API_TOKEN)
BASE_URL = "https://sids-test-env.atlassian.net"

issue_url = BASE_URL + "/rest/api/3/issue"

headers = {
   "Accept": "application/json"
}

request_body = {
    "fields": {
       "project":
       {
          "key": project_key
       },
       "summary": pr_body,
       "description": {
           "type": "doc",
           "version": 1,
           "content": [
               {
                   "type": "paragraph",
                   "content": [
                       {
                           "type": "text",
                           "text": jira_description
                       }
                   ]
               }
           ]
       }
       ,
       "issuetype": {
          "name": "Task"
       },
       "assignee": {
          "id": jira_id
       },
       "reporter": {
          "id": jira_id
       },
       "priority": {
          "name": "Low"
       }
   }
}

response = requests.request(
   "POST",
   issue_url,
   headers=headers,
   auth=auth,
   json=request_body
)

print(response.text)
issue_key = json.loads(response.text)["key"]

transitions_url = BASE_URL + f"/rest/api/3/issue/{issue_key}/transitions"

response = requests.request(
   "GET",
   transitions_url,
   auth=auth,
)

transitions_response = json.loads(response.text)
transitions = transitions_response["transitions"]
for transition in transitions:
   if transition["name"] == "Triage":
      triage_id = transition["id"]

if triage_id:
   update_json = {
      "transition": {
         "id": triage_id
      }
   }

   response = requests.request(
     "POST",
     transitions_url,
     auth=auth,
     json=update_json
   )
else: 
  print("Triage was not found in transitions, doing nothing")
