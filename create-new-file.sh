#!/bin/bash

git checkout testing-branch
mydate=$(date | sed "s/ /_/g" | sed "s/:/-/g")
git checkout -b "$mydate"

echo "hello" > $mydate.txt
git add "$mydate".txt
git commit -m "Added new file"

git push origin $mydate

git checkout main
