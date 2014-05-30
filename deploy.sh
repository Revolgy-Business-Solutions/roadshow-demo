#!/usr/bin/env bash

c="appcfg.py --oauth2 update -A roadshow-demo ."
echo -e "\nrunning command: '$c'\n"
$c
echo -e "\n\ndeploy to >>$appid<< appspot instance finished.\n"
