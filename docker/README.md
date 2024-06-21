# Docker

## Build
To build the application as a Docker, navigate to the root of this package and execute the following command
```sh
sudo docker build -t billing-experiment -f docker/Dockerfile .
```

## Run
To run a container, execute
```sh
sudo docker run -p <port>:<port> -e PRIVATE_BILLING_SERVER_TYPE=<type> billing-experiment
```
where `<type>` should be replaced with `bill`, `market` or `peer` for each of the respective servers,
and `<port>` should be replaced with the port at which the server is accessible.

## Compose
To launch the network described in the compose file, execute
```sh
sudo docker compose -f docker/docker-compose.yml up
```

## Trigger
You can use `initiator.ipynb` to trigger the different stages of the billing cycle.