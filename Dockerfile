# build requirements
FROM python:3.10.5-slim-bullseye AS builder

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
    build-essential

ENV PATH=/root/.local/bin:$PATH
COPY tilefy/requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --user -r requirements.txt


# load in main image
FROM python:3.10.5-slim-bullseye as tilefy
ARG INSTALL_DEBUG
ENV PYTHONUNBUFFERED 1

# copy build requirements
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN apt-get clean && apt-get -y update && \
    apt-get -y install --no-install-recommends \
    ttf-bitstream-vera fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# install debug tools for testing environment
RUN if [ "$INSTALL_DEBUG" ] ; then \
        apt-get -y update && apt-get -y install --no-install-recommends \
        vim htop bmon net-tools iputils-ping procps \
        && pip install --user ipython \
    ; fi

RUN mkdir /data
RUN mkdir /app

COPY tilefy /app
WORKDIR /app

RUN chmod +x ./start.sh

VOLUME /data
CMD ["./start.sh"]
