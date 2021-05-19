import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os

print(sys.argv)
if len(sys.argv) != 4:
  raise Exception("Wrong number of cmd args")

JIRA_API_EMAIL=sys.argv[2]
JIRA_API_TOKEN=sys.argv[3]
event_path = sys.argv[1]
if not os.path.isfile(event_path):
  raise Exception("Couldn't find github event file")

with open(event_path) as file:
  file_contents = file.read()
  event_obj = json.loads(file_contents)

reviewers = event_obj["pull_request"]["requested_reviewers"]
pr_body = event_obj["pull_request"]["body"]

if len(reviewers) == 0:
    raise Exception("No reviewers were assigned")

reviewer = reviewers[0]["login"]
with open("reviewers-jira-info.json") as file:
    reviewers_jira_info = json.loads(file.read())
reviewer_jira_info = reviewers_jira_info[reviewer]
project_key = reviewer_jira_info["project_key"]
jira_id = reviewer_jira_info["jira_id"]

## TODO: Put this in a secure place
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
                           "text": pr_body
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
