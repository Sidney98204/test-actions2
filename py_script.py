import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os

print(sys.argv)
if len(sys.argv) != 2:
  raise Exception("Wrong number of cmd args")
  
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

reviewer = reviewers[0]
with open("reviewers_to_teams.json") as file:
    reviewers_to_teams = json.loads(file.read())
project_key = reviewers_to_teams[reviewer]

## TODO: Put this in a secure place
auth = HTTPBasicAuth("sidneys.throwaway.email98@gmail.com", "o5ZBIy13CgO4ondBUHcCC89C")
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
          "id": "609d447f2009f100683db99d" ## TODO: Grab everyone's account IDs
       },
       "reporter": {
          "id": "5ffce992692b7901104ce6da"
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
