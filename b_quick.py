import requests
import base64
import json

fn 
token = "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"
headers = {
    'Accept': 'vnd.github.v3+json',
    'Authorization': f'token {token}',
}

file_path = ".github/reviewers-jira-info.json"
response = requests.get(
    f'https://api.github.com/repos/procurify/procurify-react/contents/{file_path}', 
    headers=headers
)
# print(response.content)
contents = response.json()["content"]
decoded = base64.b64decode(contents)
all_reviewers_info = json.loads(decoded)
print(all_reviewers_info)
