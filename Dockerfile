FROM ubuntu:20.04

RUN true \
    && apt-get -y update \
    && apt-get -y install git make gcc \
    && apt-get -y install mysql-client \
    && apt-get -y install python3 \
    && apt-get -y install pip

# Config python
ENV PYTHONPATH="${PYTHONPATH}:/project"
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install dbgen
COPY . /project
RUN make -C /project/dbgen