FROM python:3.7
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN pip install setuptools
RUN apt-get -y update
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN pip install openslide-python
RUN pip install PyYAML
RUN pip install pandas
RUN git clone "https://github.com/Pacific89/ARA-CNN" /usr/local/src
RUN pip install -r /usr/local/src/requirements.txt
RUN pip install jupyter
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# RUN nohup jupyter notebook --allow-root --no-browser > error.log &