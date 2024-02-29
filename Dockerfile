FROM public.ecr.aws/docker/library/python:3.9-slim-bullseye@sha256:c59d6aaacd1e721ffebfa50ab8991625c10a10ca5d163d130218ff047d54c8fb

RUN mkdir -p workspace
WORKDIR /workspace

RUN apt update
RUN apt install ffmpeg libsm6 libxext6 libxml2-dev libxslt-dev gcc  -y

ENV REQUIREMENTS_FILE=requirements.txt

COPY ./${REQUIREMENTS_FILE} ./requirements.txt
RUN HTTP_PROXY= HTTPS_PROXY= pip install -r requirements.txt

COPY . /workspace/

ENV PYTHONPATH $PYTHONPATH:/workspace:/workspace/src
