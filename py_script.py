import requests
from requests.auth import HTTPBasicAuth
import json
import sys
import os

print(sys.argv)
if len(sys.argv) != 2:
  raise Exception("Wrong num cmd args")
  
event_path = sys.argv[1]

if not os.path.isfile(event_path):
  raise Exception("Couldn't find file")

with open(event_path) as file:
  file_contents = file.read()
#   print("FILE CONTENTS: " + file_contents)
  json_obj = json.loads(file_contents)
  
# print(f"JSON OBJ: {json_obj}")
  
print(f'LABELS: {json_obj["pull_request"]["labels"]}')
print(f'REQUESTED REVIEWS: {json_obj["pull_request"]["requested_reviewers"]}')
print(f'BODY: {json_obj["pull_request"]["body"]}')

url = "https://sids-test-env.atlassian.net/rest/api/3/issue"

auth = HTTPBasicAuth("sidneys.throwaway.email98@gmail.com", "o5ZBIy13CgO4ondBUHcCC89C")

headers = {
   "Accept": "application/json"
}

request_body = {
    "fields": {
       "project":
       {
          "key": "GA"
       },
       "summary": "REST ye merry gentlemen.",
       "description": {
           "type": "doc",
           "version": 1,
           "content": [
               {
                   "type": "paragraph",
                   "content": [
                       {
                           "type": "text",
                           "text": "THIS IS A TEST ISSUE CREATED THRU JIRA API"
                       }
                   ]
               }
           ]
       }
       ,
       "issuetype": {
          "name": "Story"
       }
   }
}

response = requests.request(
   "POST",
   url,
   headers=headers,
   auth=auth,
   json=request_body
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
