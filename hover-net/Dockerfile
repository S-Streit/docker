FROM nvidia/cuda:10.2-cudnn7-runtime
RUN apt-get -y install bash

RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get install -y wget
RUN apt-get -y update
RUN pip install setuptools
RUN apt-get update -y
RUN pip install gdown

RUN git clone "https://github.com/vqdang/hover_net" /usr/local/src
RUN pip install -r /usr/local/src/requirements.txt

RUN gdown https://drive.google.com/u/0/uc?id=1SbSArI3KOOWHxRlxnjchO7_MbWzB4lNR -O /usr/local/models/pannuke/


ENTRYPOINT [ "bin/bash" ]