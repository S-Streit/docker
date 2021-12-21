FROM nvidia/cuda:11.4.2-devel-ubuntu20.04
ENV PATH=/root/miniconda3/bin:${PATH}

RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
RUN apt-get -y install bash
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y update
RUN apt-get install wget

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install software-properties-common
RUN apt-get -y install curl
RUN apt-get -y install python3-pip
RUN conda install -c anaconda setuptools -y

RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
RUN pip install --upgrade pip
RUN apt-get -y update
# RUN pip install opencv-python==4.5.1.48
RUN conda install -c conda-forge opencv=4.5.1 -y
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
RUN conda install -c conda-forge openslide -y
RUN conda install -c conda-forge openslide-python -y
RUN conda install pandas -y
RUN conda install -c conda-forge matplotlib -y
RUN conda install -c anaconda h5py -y
RUN conda install -c pytorch pytorch=1.1.0 -y
RUN conda install -c pytorch torchvision  -y
RUN conda install -c conda-forge pytorch-model-summary  -y
RUN apt-get -y update
RUN git clone "https://github.com/oval-group/smooth-topk.git" /usr/local/src/st
RUN python3 /usr/local/src/st/setup.py install
RUN git clone "https://github.com/Pacific89/CLAM.git" /usr/local/src/clam
RUN git clone "https://github.com/Pacific89/docker" /usr/local/wrapper
RUN ["mkdir", "/usr/local/config"]
RUN ["cp", "/usr/local/wrapper/clam/clam_command_config.json", "/usr/local/config"]

RUN conda install scipy -y
RUN conda install -U scikit-learn -y
RUN conda install PyYAML -y

RUN conda install numpy -y
RUN conda install -c conda-forge pixman -y

# RUN pip install jupyter
# RUN ["cp", "/usr/local/src/clam/clam_command_config.json", "/usr/local/config"]
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
# ENTRYPOINT [ "python", "/usr/local/wrapper/clam/start_create_patches.py" ]
ENTRYPOINT [ "bin/bash" ]