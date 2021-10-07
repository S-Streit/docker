FROM python:3.7
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN pip install setuptools
RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
RUN pip install --upgrade pip
RUN apt-get -y update
RUN pip install opencv-python==4.5.1.48
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN pip install openslide-python
RUN pip install pandas
RUN pip install matplotlib
RUN pip install h5py
RUN apt-get -y update
RUN git clone "https://github.com/oval-group/smooth-topk.git" /usr/local/src/st
RUN python /usr/local/src/st/setup.py install
RUN git clone "https://github.com/Pacific89/CLAM.git" /usr/local/src/clam
RUN pip install jupyter
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]