FROM ubuntu:20.04

RUN true \
    && apt-get -y update \
    && apt-get -y install make gcc \
    && apt-get -y install mysql-client \
    && apt-get -y install python3 \
    && apt-get -y install pip

# Config python
ENV PYTHONPATH="${PYTHONPATH}:/project"
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install dbgen
COPY . /project
RUN python3 /project/db_env/tpch/tpch_tools/tpch_tools_patch.py
RUN make -C /project/dbgen