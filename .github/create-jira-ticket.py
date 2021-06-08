import json
import sys
import os
import argparse
import requests
from requests.auth import HTTPBasicAuth
from helpers import (
   get_pull_request_info,
   create_issue_info,
   fetch_reviewers_info,
   get_reviewer_jira_info,
   search_jira_for_issue,
   create_jira_issue,
   transition_jira_issue
)


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", required=True)
parser.add_argument("-p", "--password", required=True)
parser.add_argument("-e", "--event", required=True)
parser.add_argument("-c", "--configuration", required=True)
parser.add_argument("-gu", "--github_username", required=True)
parser.add_argument("-gp", "--github_password", required=True)


io_args = parser.parse_args()
JIRA_API_EMAIL = io_args.username
JIRA_API_TOKEN = io_args.password
event_path = io_args.event
config_filepath = io_args.configuration
github_user = io_args.github_username
github_password = io_args.github_password
print(github_user)
print(github_password)

pr_info = get_pull_request_info(event_path)

issue_info = create_issue_info(pr_info)

if len(pr_info['reviewers']) == 0:
    raise Exception("No reviewers were assigned")

github_auth = (github_user, github_password)
reviewers_info = fetch_reviewers_info(config_filepath, github_auth)

jira_auth = HTTPBasicAuth(JIRA_API_EMAIL, JIRA_API_TOKEN)

for reviewer in pr_info["reviewers"]:

   reviewer_info = get_reviewer_jira_info(reviewers_info, reviewer)

   issue_exists = search_jira_for_issue(reviewer_info["project_key"], pr_info["url"], jira_auth)

   if not issue_exists:
      issue_key = create_jira_issue(
         issue_info["title"], 
         issue_info["description"], 
         reviewer_info["project_key"], 
         reviewer_info["jira_id"], 
         jira_auth)
      
      transition_jira_issue(issue_key, jira_auth)
   else:
      print("Issue already exists, skipping")
