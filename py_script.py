import requests
import json
import sys
import os

print(sys.argv)
# if len(sys.argv) != 2:
#   raise Exception("Wrong num cmd args")
  
event_path = sys.argv[1]

if not os.path.isfile(event_path):
  raise Exception("Couldn't find file")

with open(event_path) as file:
  file_contents = file.read()
  print("FILE CONTENTS: " + file_contents)
  json_obj = json.loads(file_contents)
  
print(f"JSON OBJ: {json_obj}")
  
print(json_obj["pull_request"]["labels"])
print(json_obj["pull_request"]["requested_reviewers"])
print(json_obj["pull_request"]["body"])

print("Hello world")

