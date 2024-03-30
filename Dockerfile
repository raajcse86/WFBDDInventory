FROM ubuntu:latest

WORKDIR /usr/app/src

ARG LANG='en_us.UTF-8'

# COPY requirements.txt ./requirements.txt
# RUN pip3 install -r requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-utils \
        locales \
        python3-pip \
        python3-yaml \
        rsyslog systemd systemd-cron sudo \
    && apt-get clean

RUN pip3 install --upgrade pip
RUN pip3 install streamlit
RUN pip3 install chromadb
# RUN pip3 install sentence-transformers
RUN pip3 install streamlit-tags
# RUN pip3 install torch=="1.12.1"


EXPOSE 8501
COPY / ./
ENTRYPOINT [ "streamlit","run"]
CMD [ "bddinventory.py" ]