#!/bin/bash

my_date=$(date | sed 's/ /_/g' | sed 's/:/-/g')
git checkout main
git checkout -b $my_date
echo $my_date > hello.txt
git add . && git commit -m "create test branch"
git push origin HEAD
git checkout main

