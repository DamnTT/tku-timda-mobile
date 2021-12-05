From ros:melodic-ros-core-bionic
# syntax = docker/dockerfile:experimental
# Find image form docker hub

# USER Arguments
ARG USER=docker-damn
ARG GROUP=docker-damn
ARG UID=1000
ARG GID=1000
ARG SHELL=/bin/bash
ARG ROS=ros/melodic

# There may be problems in the embedded system, which can be annit
# Env vars for the nvidia-container-runtime.
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all
SHELL ["/bin/bash","-c"]


RUN apt-get update && \
      apt-get -y install sudo

# Setup users and groups
RUN groupadd --gid ${GID} ${GROUP} \
    && useradd --gid ${GID} --uid ${UID} -ms ${SHELL} ${USER} \
    && mkdir -p /etc/sudoers.d \
    && echo "${USER}:x:${UID}:${UID}:${USER},,,:$HOME:${SHELL}" >> /etc/passwd \
    && echo "${USER}:x:${UID}:" >> /etc/group \
    && echo "${USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${USER}" \
    && chmod 0440 "/etc/sudoers.d/${USER}"

# Replace apt urls
# Change to Taiwan
RUN sed -i 's@archive.ubuntu.com@tw.archive.ubuntu.com@g' /etc/apt/sources.list
# Change to tku
#RUN sed -i 's@archive.ubuntu.com@ftp.tku.edu.tw@g' /etc/apt/sources.list

# Install packages
RUN sudo apt update && sudo apt-get install -y vim \
    && sudo apt install -y curl && sudo apt install -y autoconf automake libtool 

RUN sudo apt install -y ros-melodic-rosbridge-server ros-melodic-actionlib ros-melodic-gazebo-ros ros-melodic-roswww ros-melodic-tf2-web-republisher ros-melodic-laser-geometry ros-melodic-pcl-ros ros-melodic-move-base ros-melodic-xacro
RUN  curl -sL https://deb.nodesource.com/setup_8.x | sudo bash -
RUN sudo apt install -y byobu nodejs


RUN sudo apt install -y python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential \
    && sudo apt install -y python-rosdep \
    && sudo rosdep init \
    && rosdep update 
RUN su ${USER}
RUN echo "source /opt/ros/melodic/setup.bash"  >> ~/.bashrc \
    && echo "export ROS_MASTER_URI=http://localhost:11311" >> ~/.bashrc \
    && echo "export ROS_HOSTNAME=localhost" >> ~/.bashrc \
    && source ~/.bashrc 
COPY libmodbus.sh /home/${USER}/libmodbus.sh
Run chmod +x /home/${USER}/libmodbus.sh
Run sh /home/${USER}/libmodbus.sh 

EXPOSE 22/tcp

# Copy custom configuration scripts
#COPY config .

# RUN scripts and remove scripts

# Copy entrypoint and grant permissions

# Switch user to ${USER} and use sudo create work

# Make SSH available

# Switch to user's HOME folder

# Use CMD or ENTRYPOINT create container entry point
