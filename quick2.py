import argparse
import json
import requests
import base64

parser = argparse.ArgumentParser()
parser.add_argument("-config", "--configuration", required=True)
parser.add_argument("-gu", "--github_username", required=True)
parser.add_argument("-gp", "--github_password", required=True)


io_args = parser.parse_args()
github_user = io_args.github_username
github_password = io_args.github_password
print(github_user)
print(github_password)
print(io_args.configuration)

github_auth = (github_user, github_password)
def fetch_reviewers_info(file_path, github_auth):

    headers = {
        'Accept': 'vnd.github.v3+json',
    }

    response = requests.get(
        f'https://api.github.com/repos/Sidney98204/test-actions2/contents/{file_path}', 
        headers=headers, 
        auth=github_auth)
    # print(response.json())
    contents = response.json()["content"]
    decoded = base64.b64decode(contents)
    all_reviewers_info = json.loads(decoded)
    return all_reviewers_info

r = fetch_reviewers_info(".github/reviewers-info.json", github_auth)
print(r)

