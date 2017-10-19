# This file is a template, and might need editing before it works on your project.
FROM continuumio/miniconda:latest

RUN apt-get update
RUN apt-get -y install freeglut3-dev

# RUN conda create --name phenome python --yes
# RUN /bin/bash -c "source activate phenome"

RUN echo "Dependency"
RUN conda install numpy --yes
RUN conda install opencv --yes
RUN conda install scipy --yes
RUN conda install scikit-learn --yes
RUN conda install networkx --yes
RUN conda install vtk --yes
RUN conda install scikit-image --yes

RUN echo "Optional dependency"
RUN conda install jupyter --yes
RUN conda install nose --yes
RUN conda install coverage --yes
RUN conda install matplotlib --yes

#RUN mkdir -p /home/phenomenal
#WORKDIR /home/phenomenal
#COPY . /home/phenomenal
#RUN chmod -R -x test/

#RUN python setup.py develop --prefix=$CONDA_PREFIX

RUN python -c "import cv2"

CMD ["bash"]