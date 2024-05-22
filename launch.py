import sys
from time import sleep
import logging
from socketserver import BaseRequestHandler, TCPServer
from threading import Thread
from private_billing.messages import BootMessage
from private_billing.server.message_handler import MessageSender, Target
from src.experiment import (
    ExperimentServer,
    ExperimentOperator,
    ExperimentPeer,
    ExperimentOperatorDataStore,
)


def launch_server(address, market_address, handler: BaseRequestHandler):
    def serve():
        with TCPServer(address, handler, True) as server:
            print(f"serving on {address}")
            server.serve_forever()

    # Launch server
    thread = Thread(target=serve)
    thread.start()

    # Allow server to boot up
    sleep(0.5)

    # Send boot message
    msg = BootMessage(market_address)
    server = Target(None, address)
    resp = MessageSender.send(msg, server)
    logger.debug(f"booted server: {resp}")


def launch_market(address, cyc_len, handler: BaseRequestHandler):
    with TCPServer(address, handler, True) as server:
        print(f"serving on {address}")

        # Setup server
        mods = ExperimentOperatorDataStore()
        mods.cycle_length = cyc_len
        server.data = mods

        # Launch
        server.serve_forever()


if __name__ == "__main__":
    type_ = sys.argv[1]

    # Specify logging setup
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Settings
    cyc_len = 672  # nr of 15m slots in a week.

    market_address = "0.0.0.0", 5559
    match type_:
        case "bill":
            address = "0.0.0.0", 5554
            launch_server(address, market_address, ExperimentServer)
        case "peer":
            address = "0.0.0.0", 5565
            launch_server(address, market_address, ExperimentPeer)
        case "market":
            launch_market(market_address, cyc_len, ExperimentOperator)
        case _:
            raise ValueError(f"{type_} is invalid type")
