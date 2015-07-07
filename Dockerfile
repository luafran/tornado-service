# HTTP echo service

# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Luciano Afranllie <luafran@gmail.com>

# Labels
LABEL name=tornado-service version=1.0.0

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libcurl4-openssl-dev \
    libev4 libev-dev python \
    python-dev \
    python-distribute \
    python-pip

# Deploy application
# RUN mkdir /var/log/tornadoservice/
COPY ./ /tmp/build/
WORKDIR /tmp/build/common_pkg
RUN python setup.py sdist --dist-dir ../dist
WORKDIR /tmp/build/service1_pkg
RUN python setup.py sdist --dist-dir ../dist
WORKDIR /tmp/build
RUN pip install dist/prjname-common-0.1.0.tar.gz \
    && pip install dist/prjname-service1-1.0.0.tar.gz \
    && rm -rf /tmp/build

# Expose port
EXPOSE 8080

# Run app
ENTRYPOINT ["prjname-runservice"]
CMD ["service1", "--port", "8080"]
