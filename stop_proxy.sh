#!/usr/bin/env bash
tokill=`ps -ef | grep ffmpeg | grep 'rtsp' | awk '{print $2}'`
kill -9 $tokill
