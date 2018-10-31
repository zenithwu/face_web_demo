#!/usr/bin/env bash
tokill=`ps -ef | grep python | grep 'face_check.py' | awk '{print $2}'`
kill -9 $tokill
