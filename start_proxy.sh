nohup /usr/local/ffmpeg/bin/ffmpeg -f rtsp -rtsp_transport tcp -i rtsp://show_face:face_show@863@192.168.0.215:554/h264/ch1/main/av_stream -codec copy -f flv -an rtmp://192.168.0.203:1935/hls/test -s 1280*720 >> ffmpeg.log 2>&1 &