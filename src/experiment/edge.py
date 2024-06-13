from pathlib import Path
import pickle
from private_billing.edge_server import EdgeServer
from private_billing.network import NodeInfo, no_verification_required, replies
from private_billing.messages import ContextMessage, HiddenBillMessage
from private_billing.core import CycleID, CycleContext

from .experiment import (
    BootStrapMessage,
    ExperimentMessageType,
    speedtest,
)
from .telemetry import (
    TelemetryDataStore,
    TelemetryType,
    TelemetryMessage,
    GetTelemetryMessage,
)
from private_billing.log import full_stack, logger


class ExperimentEdge(EdgeServer):

    def __post_init__(self):
        super().__post_init__()
        self.telemetry_store = TelemetryDataStore()
        self.current_cycle = -1
        self.context_data_file: Path = None

    @property
    def handlers(self):
        return {
            **super().handlers,
            ExperimentMessageType.START_BOOTSTRAP: self.handle_start_bootstrap,
            ExperimentMessageType.TELEMETRY: self.handle_telemetry,
            ExperimentMessageType.GET_TELEMETRY: self.handle_get_telemetry,
        }

    @no_verification_required
    def handle_start_bootstrap(self, msg: BootStrapMessage, origin: NodeInfo) -> None:
        """
        Handle request to start boot strapping.
        This message is the kick-off to the experiment.
        """
        # Tell all peers to start bootstrapping
        peers = set(self.network_peers).difference(self.network_edges)
        self.broadcast(msg, peers)

    def handle_telemetry(self, msg: TelemetryMessage, origin: NodeInfo) -> None:
        """Handle incoming telemetry information."""
        self.telemetry_store.store(msg, origin)

        # Check if round is done
        # If so, use this as cue to start the next round.
        if not self._current_cycle_is_finished():
            return

        # Progress to next round
        self.current_cycle += 1
        self._broadcast_context()

    @replies
    @no_verification_required
    def handle_get_telemetry(self, msg: GetTelemetryMessage, origin: NodeInfo) -> None:
        """
        Handle 'get telemetry' request.
        This handle enables getting telemetry data from the server.
        """
        try:
            cycle_id = msg.cycle_id
            cycle_data = self.telemetry_store.aggregate(cycle_id)
            response = TelemetryMessage(
                self.address, -1, cycle_id, TelemetryType.AGGREGATE, cycle_data
            )
            self.reply(response)
        except Exception as e:
            logger.error(str(e))
            logger.debug(full_stack())

    def _broadcast_context(self) -> None:
        """
        Broadcast CycleContext of current cycle to all participants.
        This starts this round.
        """
        context = self._load_context(self.current_cycle)
        msg = ContextMessage(context)
        self.broadcast(msg, self.network_edges)

    def _current_cycle_is_finished(self) -> bool:
        """Returns whether the current cycle is finished."""
        current_cycle = self.current_cycle
        cycle_telemetry_data = self.telemetry_store.get(current_cycle)

        if current_cycle < 0:
            # Check if all peers submitted decrypt data
            keys = [(TelemetryType.BOOTSTRAP, ip) for ip in self.network_cores]
        else:
            # Check if all peers submitted decrypt data
            keys = [(TelemetryType.DECRYPT, ip) for ip in self.network_cores]

        all_submitted = all(map(lambda key: key in cycle_telemetry_data, keys))
        return all_submitted

    def _load_context(self, cycle_id: CycleID) -> CycleContext:
        """
        Load context from file.

        :param cycle_id: id of cycle to load
        :return: loaded cycle context
        """
        data: list = pickle.load(self.context_data_file)
        return data[cycle_id]

    def run_billing(self, cycle_id: CycleID) -> None:
        bills, time = speedtest(self.shared_biller.compute_bills, cycle_id)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.address, self.id, cycle_id, TelemetryType.COMPUTE_BILL, time
        )
        self.handle_telemetry(telemetry_msg, self._node_info)
        
        return bills        
