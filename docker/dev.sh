#!/bin/bash
WORK_ENV=/home/damn/timda-mobile/src
USER=docker-damn
#docker run -it -v ${WORK_ENV}:/home/${USER}/timda-mobile/src ros-env 
docker run -it -v ${WORK_ENV}:/root/timda-mobile/src ros-env 
