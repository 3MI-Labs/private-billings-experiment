from pathlib import Path
import pickle
import time
from private_billing import CoreServer
from private_billing import CycleID, Data
from private_billing.core.hiding import HidingContext
from private_billing.network import NodeInfo, PeerToPeerBillingBaseServer, no_verification_required
from private_billing.messages import (
    BillMessage,
    ConnectMessage,
    DataMessage,
    SeedMessage,
    ContextMessage,
)
from .experiment import (
    BootStrapMessage,
    ExperimentMessageType,
    speedtest,
)
from .telemetry import TelemetryType, TelemetryMessage

class ExperimentCore(CoreServer):
    
    def __post_init__(self) -> None:
        super().__post_init__()
        self.bootstrap_start = None
        self.consumption_data_file: Path = None

    @property
    def handlers(self):
        new_handlers = {
            ExperimentMessageType.START_BOOTSTRAP: self.handle_start_bootstrap,
        }
        return {**super().handlers, **new_handlers}
    
    @no_verification_required
    def handle_connect(self, msg: ConnectMessage, origin: NodeInfo) -> None:
        PeerToPeerBillingBaseServer.handle_connect(self, msg, origin)

        cycle_length = msg.billing_state.get("cycle_length")
        if cycle_length and not self.hc:
            self.hc = HidingContext(cycle_length, self.mg)

        # Do not send seed to peers

    ### Handle bootstrap message

    @no_verification_required
    def handle_start_bootstrap(self, msg: BootStrapMessage, origin: NodeInfo):
        """Handle signal to start the bootstrapping procedure."""
        # Keep track of when bootstrapping started
        self.bootstrap_start = time.process_time()

        # Send seeds to all connected peers
        for peer in self.network_cores:
            self.try_send_seed(peer)

    ### Handle incoming seed message

    def handle_seed(self, msg: SeedMessage, origin: NodeInfo) -> None:
        super().handle_seed(msg, origin)

        # See if we received all seeds
        if not self.hc.is_ready:
            return

        # Send telemetry data to edge
        bootstrap_end = time.process_time()
        bootstrap_time = bootstrap_end - self.bootstrap_start
        telemetry_msg = TelemetryMessage(
            self.id, -1, TelemetryType.BOOTSTRAP, bootstrap_time
        )
        self.broadcast(telemetry_msg, self.network_edges)

    @no_verification_required
    def handle_cycle_context(self, msg: ContextMessage, origin: NodeInfo) -> None:
        """Handle incoming CycleContext"""
        context = msg.context

        # Use this as a cue to start sending data for the specified cycle.
        data = self.load_data(context.cycle_id)

        # Encrypt data
        hidden_data, hiding_time = speedtest(data.hide, self.hc)

        # Send out data
        data_msg = DataMessage(hidden_data)
        self.broadcast(data_msg, self.network_edges)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.id, hidden_data.cycle_id, TelemetryType.ENCRYPT, hiding_time
        )
        self.broadcast(telemetry_msg, self.network_edges)

    def handle_hidden_bill(self, msg: BillMessage, origin: NodeInfo):
        _, reveal_time = speedtest(super().handle_hidden_bill, msg, origin)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.id, msg.bill.cycle_id, TelemetryType.DECRYPT, reveal_time
        )
        self.broadcast(telemetry_msg, self.network_edges)

    def load_data(self, cycle_id: CycleID) -> Data:
        """Load data from file"""
        data: list = pickle.load(self.consumption_data_file)
        return data[cycle_id]
