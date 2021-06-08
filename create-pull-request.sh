#!/bin/bash

git checkout main
branch_name=$(date | sed 's/:/_/g' | sed 's/ /_/g')
git checkout -b $branch_name
echo "hello world" > test-file.txt
git add . && git commit -m "new file"
git push origin $branch_name
git checkout main