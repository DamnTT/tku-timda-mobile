#!/bin/bash
WORK_ENV=/home/damn/timda-mobile/src
USER=docker-damn
#docker run -it -v ${WORK_ENV}:/home/${USER}/timda-mobile/src ros-env 
#docker run -it -v ${WORK_ENV}:/root/timda-mobile/src ros-env 
docker run -it \
  --runtime=nvidia \
  -v /etc/localtime:/etc/localtime:ro \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=unix$DISPLAY \
  -e GDK_SCALE \
  -e GDK_DPI_SCALE \
  -v ${WORK_ENV}:/root/timda-mobile/src \
  -v dev-db:/root/timda-mobile/ \
  --name timda-mobile \
  -p 8001:8001 \
  -p 80:80 \
  ros-env
