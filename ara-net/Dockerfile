FROM python:3.7
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN pip install setuptools
RUN apt-get -y update
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN apt install -y libblas3 liblapack3 liblapack-dev libblas-dev
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt install -y gfortran
RUN pip install openslide-python
RUN pip install PyYAML
RUN pip install pandas
RUN git clone "https://github.com/Pacific89/ARA-CNN" /usr/local/src
RUN pip install -r /usr/local/src/requirements.txt
RUN pip install numpy==1.17.3
RUN pip install spams
RUN pip install staintools
RUN ["mkdir", "/usr/local/config"]
RUN ["cp", "/usr/local/src/ara_command_config.json", "/usr/local/config"]
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# ENTRYPOINT [ "python", "/usr/local/src/src/start_ara.py" ]
ENTRYPOINT [ "bin/bash" ]
# RUN pip install jupyter
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# RUN nohup jupyter notebook --allow-root --no-browser > error.log &