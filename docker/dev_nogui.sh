#!/bin/bash
WORK_ENV=/home/damn/timda-mobile/src
USER=docker-damn
#docker run -it -v ${WORK_ENV}:/home/${USER}/timda-mobile/src ros-env 
#docker run -it -v ${WORK_ENV}:/root/timda-mobile/src ros-env 
docker run -it \
  --runtime=nvidia \
  -v /etc/localtime:/etc/localtime:ro \
  -v ${WORK_ENV}:/root/timda-mobile/src \
  -v dev-db:/root/timda-mobile/ \
  --name timda-mobile \
  -p 8001:8001 \
  -p 8081:8081 \
  -p 8082:8082 \
  -p 8083:8083 \
  -p 80:80 \
  ros-env
