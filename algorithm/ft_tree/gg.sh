#!/bin/bash
git pull origin master
git add .
git commit -m "$1"
git push origin master
