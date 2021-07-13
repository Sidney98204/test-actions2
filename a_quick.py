import requests
import json

x = ""
for i in range(1):
    query = """query {
  users(first: 200) {
    nodes {
      name
      id
    }
  }
}"""
    headers = {
        'Accept': 'application/json',
        "Authorization": "24MuxhDjZ496vjDCP89Tk1BbsraaKs3z8xpXpVaF"
    }
    response = requests.post('https://api.linear.app/graphql', headers=headers, json={"query": query})
    print(response.text)
    print(response.json())