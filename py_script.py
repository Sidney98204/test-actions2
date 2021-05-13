import requests
import json
import sys
import os

if len(sys.argv) != 2:
  raise Exception("Wrong num cmd args")
  
event_path = sys.argv[1]

if not os.path.isfile(event_path):
  raise Exception("Couldn't find file")

with open(event_path) as file:
  file_contents = file.read()
  json_obj = json.loads(file_contents)
  
print(json_obj["labels"])
print(json_obj["requested_reviewers"])

print("Hello world")

