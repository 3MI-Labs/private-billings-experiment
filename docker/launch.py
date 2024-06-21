from pathlib import Path
import logging
from private_billing.server.request_reply import TCPAddress
from src.experiment import ExperimentCore, ExperimentEdge
import os
from private_billing.log import logger

logger.setLevel(os.environ.get("LOG_LEVEL", logging.DEBUG))


def launch_core(address: TCPAddress) -> None:
    core = ExperimentCore(address)

    # Get edge address
    edge_host = os.environ.get("EDGE_HOST", "edge")
    edge_port = int(os.environ.get("EDGE_PORT", 5555))
    edge_address = TCPAddress(edge_host, edge_port)

    # Setup data file
    data_file = Path(os.environ.get("CORE_DATA_LOCATION"))
    core.consumption_data_file = data_file
    # Start
    logger.debug(f"booting core @ {address}...")
    core.start(edge_address)


def launch_edge(address: TCPAddress) -> None:
    # Launch edge
    cyc_len = int(os.environ.get("CYCLE_LENGTH", 672))
    edge = ExperimentEdge(address, cyc_len)
    logger.debug(f"booting edge @ {address}...")
    edge.start()


if __name__ == "__main__":
    server_type = os.environ.get("SERVER_TYPE")

    # Address
    host = os.environ.get("HOST")
    port = int(os.environ.get("PORT"))
    address = TCPAddress(host, port)

    print(type(server_type), server_type)

    match server_type:
        case "core":
            launch_core(address)
        case "edge":
            launch_edge(address)
        case _:
            raise ValueError(f"{server_type}, {type(server_type)} is invalid type")
