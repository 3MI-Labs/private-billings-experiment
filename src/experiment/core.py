from pathlib import Path
import pickle
import time
from private_billing import CoreServer
from private_billing import CycleID, Data
from private_billing.core import HiddenData
from private_billing.core.hiding import HidingContext
from private_billing.core.utils import vector
from private_billing.network import (
    NodeInfo,
    PeerToPeerBillingBaseServer,
    no_verification_required,
)
from private_billing.messages import (
    BillMessage,
    ConnectMessage,
    DataMessage,
    HiddenBillMessage,
    HiddenDataMessage,
    SeedMessage,
    ContextMessage,
)
from .experiment import (
    BootStrapMessage,
    ExperimentMessageType,
    speedtest,
)
from .telemetry import TelemetryType, TelemetryMessage
from private_billing.log import full_stack, logger


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
        peers = set(self.network_peers).difference(self.network_edges)
        for peer in peers:
            self.try_send_seed(peer)

        # See if we received all seeds
        if self.finalized_seed_exchange:
            self.send_bootstrap_telemetry()

    def send_bootstrap_telemetry(self) -> None:
        # Send telemetry data to edge
        bootstrap_end = time.process_time()
        bootstrap_time = bootstrap_end - self.bootstrap_start
        telemetry_msg = TelemetryMessage(
            self.address, self.id, -1, TelemetryType.BOOTSTRAP, bootstrap_time
        )
        self.broadcast(telemetry_msg, self.network_edges)

    @property
    def finalized_seed_exchange(self):
        nr_seeds = len(self.hc.mask_generator.owned_seeds)
        expected_nr_seeds = len(list(self.network_cores)) - 1
        logger.debug(f"thusfar received {nr_seeds=}/{expected_nr_seeds}")
        return nr_seeds == expected_nr_seeds

    ### Handle incoming seed message

    def handle_seed(self, msg: SeedMessage, origin: NodeInfo) -> None:
        super().handle_seed(msg, origin)

        # See if we received all seeds
        if not self.hc.is_ready:
            return

        # See if we received all seeds
        if self.finalized_seed_exchange:
            self.send_bootstrap_telemetry()

    @no_verification_required
    def handle_cycle_context(self, msg: ContextMessage, origin: NodeInfo) -> None:
        """Handle incoming CycleContext"""
        context = msg.context

        # Use this as a cue to start sending data for the specified cycle.
        logger.info("loading data")
        data = self.load_data(context.cycle_id)
        self.handle_data(DataMessage(None, data), origin)

    def hide_data(self, data: Data) -> HiddenData:
        """Send telemetry about data hiding prodecure"""
        hidden_data, hiding_time = speedtest(super().hide_data, data)

        # Send telemetry data about this procedure
        telemetry_msg = TelemetryMessage(
            self.address,
            self.id,
            hidden_data.cycle_id,
            TelemetryType.ENCRYPT,
            hiding_time,
        )
        self.broadcast(telemetry_msg, self.network_edges)

        return hidden_data

    def handle_hidden_bill(self, msg: HiddenBillMessage, origin: NodeInfo):
        try:
            _, reveal_time = speedtest(super().handle_hidden_bill, msg, origin)

            # Send telemetry data
            telemetry_msg = TelemetryMessage(
                self.address,
                self.id,
                msg.hidden_bill.cycle_id,
                TelemetryType.DECRYPT,
                reveal_time,
            )
            self.broadcast(telemetry_msg, self.network_edges)
        except Exception as e:
            logger.error(str(e))
            logger.debug(full_stack())

    def load_data(self, cycle_id: CycleID) -> Data:
        """Load data from file"""
        import json

        with self.consumption_data_file.open() as fp:
            data = json.load(fp)
        utilizations = vector(data["utilization"].values())
        promises = vector(data["utilization promise"].values())
        return Data(self.id, cycle_id, promises, utilizations)
