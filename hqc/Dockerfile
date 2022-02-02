FROM python:3.7
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y update
RUN apt-get -y install git
RUN pip install setuptools
RUN apt-get -y update
RUN apt-get install -y wget
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN pip install openslide-python
RUN mkdir -p /usr/local/config
# RUN mkdir -p /usr/local/wrapper
RUN git clone "https://github.com/Pacific89/HistoQC" /usr/local/src
# RUN cd /usr/local/src; wget "https://github.com/Pacific89/HistoQC"
RUN pip install -r /usr/local/src/requirements.txt
RUN pip install tensorflow==1.13.1
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install opencv-python
RUN echo hello?!!!?!!!!!!!!!!!!!!
RUN git clone "https://github.com/Pacific89/docker" /usr/local/wrapper
# RUN ["cp", "/usr/local/wrapper/hqc/config_light.ini", "/usr/local/config"]
# RUN ["cp", "/usr/local/wrapper/hqc/default_command_config.json", "/usr/local/config"]
# CMD ["bin/bash"]
# CMD [ "python /usr/local/src/start_hqc.py" ]
# RUN ["cp", "/usr/local/src/hqc_command_config.json", "/usr/local/config"]
# CMD [ "python /usr/local/src/start_hqc.py" ]
ENTRYPOINT [ "python", "/usr/local/wrapper/start_wrapper.py" ]
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# RUN jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password='' &