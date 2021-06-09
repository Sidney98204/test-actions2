import requests
import base64
import json

headers = {
    'Accept': 'vnd.github.v3+json',
}
auth = ("Sidney98204", "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")

path = ".github/reviewers-jira-info.json"
response = requests.get(f'https://api.github.com/repos/procurify/procurify-react/contents/{path}', headers=headers, auth=auth)
# response = requests.get(f'https://api.github.com/repos/Sidney98204/test-actions2/contents/{path}', headers=headers, auth=auth)
print(response.json())

contents = response.json()["content"]
decoded = base64.b64decode(contents)
print(decoded)
config = json.loads(decoded)
print(config)

