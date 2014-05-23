#!/usr/bin/env bash

if [ "x$1" == "x" ] ; then
    echo "App ID required."
    exit
fi

appid=$1
c="appcfg.py --oauth2 update -A $appid ."
echo "\nrunning command: '$c'\n"
$c
echo "\n\ndeploy to >>$appid<< appspot instance finished."