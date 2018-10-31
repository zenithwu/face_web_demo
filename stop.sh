#!/usr/bin/env bash
tokill=`ps -ef | grep python | grep 'application.py' | awk '{print $2}'`
kill -9 $tokill
