FROM nvidia/cuda:10.2-cudnn7-runtime
RUN apt-get -y install bash

RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install software-properties-common
RUN apt-get -y install curl
RUN apt-get -y install python3-pip
RUN pip3 install Pillow==6.2.2
RUN pip3 install setuptools
RUN apt-get -y update
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN pip3 install openslide-python
RUN pip3 install PyYAML
RUN pip3 install pandas
RUN git clone "https://github.com/Pacific89/ARA-CNN" /usr/local/src
RUN pip3 install -r /usr/local/src/requirements.txt
RUN ["mkdir", "/usr/local/config"]
RUN ["cp", "/usr/local/src/ara_command_config.json", "/usr/local/config"]
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
ENTRYPOINT [ "python3", "/usr/local/src/src/start_ara.py" ]

# RUN pip install jupyter
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# RUN nohup jupyter notebook --allow-root --no-browser > error.log &


