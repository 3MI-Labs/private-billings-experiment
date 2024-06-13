from pathlib import Path
import logging
from private_billing.server.request_reply import TCPAddress
from src.experiment import ExperimentCore, ExperimentEdge
import os
from private_billing.log import logger

logger.setLevel(os.environ.get("DEBUG_LEVEL", logging.DEBUG))


def launch_core(address: TCPAddress) -> None:
    core = ExperimentCore(address)

    # Get market address
    market_host = os.environ.get("MARKET_HOST", "market")
    market_port = int(os.environ.get("MARKET_PORT", 5555))
    market_address = TCPAddress(market_host, market_port)

    # Setup data file
    data_file = Path(os.environ.get("PEER_DATA_LOCATION"))
    core.consumption_data_file = data_file

    # Start
    logger.debug(f"booting core @ {address}...")
    core.start(market_address)


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

    match server_type:
        case "core":
            launch_core(address)
        case "edge":
            launch_edge(address)
        case _:
            raise ValueError(f"{server_type} is invalid type")
