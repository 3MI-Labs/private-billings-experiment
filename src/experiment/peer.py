from pathlib import Path
import pickle
import time
from private_billing import CycleID, Data, Peer, PeerDataStore
from private_billing.server import Target, MessageSender
from private_billing.messages import (
    BillMessage,
    DataMessage,
    SeedMessage,
    ContextMessage,
)

from .experiment import (
    BootStrapMessage,
    ExperimentMessageType,
    TelemetryMessage,
    speedtest,
)
from .telemetry import TelemetryType


class ExperimentPeerDataStore(PeerDataStore):

    def __init__(self):
        super().__init__()
        self.consumption_data_file: Path = None


class ExperimentPeer(Peer):

    @property
    def data(self):
        return ExperimentPeerDataStore()

    @property
    def handlers(self):
        new_handlers = {
            ExperimentMessageType.START_BOOTSTRAP: self.handle_start_bootstrap,
        }
        return {**super().handlers, **new_handlers}

    def handle_start_bootstrap(self, msg: BootStrapMessage, sender: Target):
        """Handle signal to start the bootstrapping procedure."""
        # Keep track of when bootstrapping started
        self.data.bootstrap_start = time.clock()

        # Send seeds to all connected peers
        for peer in self.data.peers.values():
            self._send_seed(peer)

    def handle_receive_seed(self, msg: SeedMessage, sender: Target):
        super().handle_receive_seed(msg, sender)

        # See if we received all seeds
        if not self.data.hc.is_ready:
            return

        # Send telemetry data
        bootstrap_end = time.clock()
        bootstrap_time = bootstrap_end - self.data.bootstrap_start
        telemetry_msg = TelemetryMessage(
            self.data.id, -1, TelemetryType.BOOTSTRAP, bootstrap_time
        )
        MessageSender.send(telemetry_msg, self.data.market_operator)

    def _include_peer(self, peer: Target) -> None:
        """
        Overriding this function;
        in the experiment we are only sending seeds after receiving the proper
        signal
        """
        pass

    def handle_receive_context(self, msg: ContextMessage) -> None:
        """
        Handle incoming CycleContext

        :param msg: Message containing context information
        """
        super().handle_receive_context(msg)
        context = msg.context

        # Use this as a cue to start sending data for the specified cycle.
        data = self.load_data(context.cycle_id)

        # Encrypt data
        hidden_data, hiding_time = speedtest(data.hide, self.data.hc)

        # Send out data
        data_msg = DataMessage(hidden_data)
        MessageSender.send(data_msg, self.data.billing_server)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.data.id, hidden_data.cycle_id, TelemetryType.ENCRYPT, hiding_time
        )
        MessageSender.send(telemetry_msg, self.data.market_operator)

    def handle_receive_bill(self, msg: BillMessage, sender: Target):
        _, reveal_time = speedtest(super().handle_receive_bill, msg, sender)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.data.id, msg.bill.cycle_id, TelemetryType.DECRYPT, reveal_time
        )
        MessageSender.send(telemetry_msg, self.data.market_operator)

    def load_data(self, cycle_id: CycleID) -> Data:
        """Load data from file"""
        data: list = pickle.load(self.data.consumption_data_file)
        return data[cycle_id]
