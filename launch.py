from pathlib import Path
import sys
from private_billing.server import TCPAddress
from src.experiment import ExperimentEdge, ExperimentCore
from private_billing.log import logger


def launch_core(address: TCPAddress, args) -> None:
    core = ExperimentCore(address)

    # Get market address
    market_host = args[4] or "localhost"
    market_port = int(args[5] or 5555)
    market_address = TCPAddress(market_host, market_port)

    # Setup data file
    data_file = Path(args[6] or "data/user_0.json")
    core.consumption_data_file = data_file

    # Start
    logger.debug(f"booting core @ {address}...")
    core.start(market_address)


def launch_edge(address: TCPAddress, args) -> None:
    # Launch edge
    cyc_len = int(args[4] or 672)
    edge = ExperimentEdge(address, cyc_len)
    logger.debug(f"booting edge @ {address}...")
    edge.start()


if __name__ == "__main__":
    args = sys.argv + [None] * 5
    type_ = args[1]
    host = args[2] or "localhost"
    port = int(args[3] or 5555)
    address = TCPAddress(host, port)

    match type_:
        case "core":
            launch_core(address, args)
        case "edge":
            launch_edge(address, args)
        case _:
            raise ValueError(f"{type_} is invalid type")
