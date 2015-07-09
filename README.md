# Tornado Skeleton Service

Skeleton for web services implemented using tornado.

Clone this repo.

Install OS dependencies.
(May be some dependency is missing since setup.sh was not tested in a clean environment yet)

```shell
$ sudo ./install_os_dependencies.sh
`````

Generate environments

```shell
$ tox -r
`````

Run service using tox

```shell
$ tox -e runservice
```````````

Send a request to service health

```shell
$ curl --proxy '' 'http://localhost:10001/health?include_details=true' 
```````````

Build docker image

```shell
$ sudo docker build -t quay.io/luafran/tornado-service . 
```````````

Run docker image

```shell
$ sudo docker run -p 10001:10001 -d -e MFS_ENV=test --name tornado-service quay.io/luafran/tornado-service
```````````

