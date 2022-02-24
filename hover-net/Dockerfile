FROM nvidia/cuda:11.4.2-devel-ubuntu20.04
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y install bash
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install software-properties-common
RUN apt-get -y install curl
RUN apt-get -y install python3-pip
RUN pip install setuptools
RUN apt-get update -y
RUN pip install gdown
RUN pip install torch

RUN apt-get install libsm6 libxrender1 libfontconfig1 -y
RUN pip install opencv-python
RUN apt install -y openslide-tools
RUN pip install openslide-python
RUN pip install h5py

RUN gdown https://drive.google.com/u/0/uc?id=1SbSArI3KOOWHxRlxnjchO7_MbWzB4lNR -O /usr/local/models/pannuke/

RUN git clone "https://github.com/Pacific89/hover_net" /usr/local/src
RUN pip install -r /usr/local/src/requirements.txt
RUN pip install docker-py

RUN echo Hello!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
RUN git clone "https://github.com/Pacific89/docker" /usr/local/wrapper
RUN ["cp", "/usr/local/wrapper/hover-net/default_command_config.json", "/usr/local/wrapper"]

ENTRYPOINT [ "python3", "/usr/local/wrapper/start_wrapper.py"]

# ENTRYPOINT [ "bin/bash" ]