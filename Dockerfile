FROM public.ecr.aws/docker/library/python:3.9-slim-bullseye

RUN mkdir -p workspace
WORKDIR /workspace

RUN apt update
RUN apt install ffmpeg libsm6 libxext6 libxml2-dev libxslt-dev  -y

ENV REQUIREMENTS_FILE=requirements.txt

COPY ./${REQUIREMENTS_FILE} ./requirements.txt
RUN HTTP_PROXY= HTTPS_PROXY= pip install -r requirements.txt

COPY . /workspace/

ENV PYTHONPATH $PYTHONPATH:/workspace:/workspace/src
