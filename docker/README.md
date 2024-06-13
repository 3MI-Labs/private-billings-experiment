# Docker

To build the application as a Docker, navigate to the root of this package and execute the following command
```sh
sudo docker build -t billing-experiment -f docker/Dockerfile .
```

To spawn a container, execute
```sh
sudo docker run -p <port>:<port> -e PRIVATE_BILLING_SERVER_TYPE=<type> billing-experiment
```
where `<type>` should be replaced with `bill`, `market` or `peer` for each of the respective servers,
and `<port>` should be replaced with the port at which the server is accessible.
