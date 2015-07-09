FROM ubuntu:14.04

MAINTAINER Luciano Afranllie <luafran@gmail.com>

# ENV http_proxy=http://proxy-us.intel.com:911 https_proxy=http://proxy-us.intel.com:911

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
WORKDIR /tmp/build
RUN python setup.py sdist --dist-dir ./dist
RUN pip install dist/prjname-service1-1.0.0.tar.gz \
    && rm -rf /tmp/build

# Expose port
EXPOSE 10001

# Run app
ENTRYPOINT ["prjname-runservice"]
CMD ["service1", "--port", "10001"]
