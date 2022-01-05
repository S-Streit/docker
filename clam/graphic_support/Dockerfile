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
    && mkdir /root/.pip \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install software-properties-common
RUN apt-get -y install curl
RUN apt-get -y install python3-pip
RUN pip install setuptools

RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y
RUN apt-get install 'ffmpeg'\
    'libsm6'\
    'libxext6'  -y
RUN pip install --upgrade pip
RUN apt-get -y update
# RUN pip install opencv-python==4.5.1.48
RUN pip install opencv-python==4.5.1.48
RUN apt-get install -y ca-certificates
RUN apt install -y openslide-tools
# RUN pip install openslide
RUN pip install openslide-python
RUN pip install pandas
RUN pip install matplotlib
RUN pip install h5py
# RUN pip install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch -y
RUN pip install torch
RUN pip install torchvision
RUN pip install torchsummary
# RUN pip install -c pip-forge pytorch-model-summary  -y
RUN apt-get -y update
RUN mkdir -p /root/.cache/torch/hub/checkpoints
RUN wget https://download.pytorch.org/models/resnet50-19c8e357.pth -O /root/.cache/torch/hub/checkpoints/resnet50-19c8e357.pth

RUN git clone "https://github.com/oval-group/smooth-topk.git" /usr/local/st
RUN python3 /usr/local/st/setup.py install

RUN pip install scipy
RUN pip install scikit-learn
RUN pip install pyyaml

RUN pip install numpy
RUN conda install -c conda-forge pixman -y

RUN git clone "https://github.com/Pacific89/CLAM.git" /usr/local/src
RUN echo Hello!?!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
RUN git clone "https://github.com/Pacific89/docker" /usr/local/wrapper
# RUN ["mkdir", "/usr/local/config"]
# RUN ["cp", "/usr/local/wrapper/clam/clam_command_config.json", "/usr/local/config"]

# RUN pip install jupyter
# RUN ["cp", "/usr/local/src/clam/clam_command_config.json", "/usr/local/config"]
# CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
ENTRYPOINT [ "python", "/usr/local/wrapper/start_wrapper.py" ]
# ENTRYPOINT [ "bin/bash" ]