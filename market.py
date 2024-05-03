from pathlib import Path
import pickle
from private_billing import MarketOperator
from private_billing.market import MarketOperatorDataStore
from private_billing.server import Target, MessageSender
from private_billing.messages import ContextMessage
from private_billing.core import CycleID, CycleContext

from .experiment import (
    BootStrapMessage,
    ExperimentMessageType,
    GetTelemetryMessage,
    TelemetryMessage,
)
from .telemetry import TelemetryDataStore, TelemetryType


class ExperimentOperatorDataStore(MarketOperatorDataStore):

    def __init__(self):
        super().__init__()
        self.telemetry_store = TelemetryDataStore()
        self.current_cycle = -1
        self.context_data_file: Path = None


class ExperimentOperator(MarketOperator):

    @property
    def data(self) -> ExperimentOperatorDataStore:
        return ExperimentOperatorDataStore()

    @property
    def handlers(self):
        new_handlers = {
            ExperimentMessageType.START_BOOTSTRAP: self.handle_start_bootstrap,
            ExperimentMessageType.TELEMETRY: self.handle_telemetry,
            ExperimentMessageType.GET_TELEMETRY: self.handle_get_telemetry,
        }
        return {**super().handlers, **new_handlers}

    def handle_start_bootstrap(self, msg: BootStrapMessage, sender: Target) -> None:
        """
        Handle request to start boot strapping.
        This message is the kick-off to the experiment.
        """
        # Tell all peers to start bootstrapping
        for peer in self.data.participants:
            MessageSender.send(msg, peer)

    def handle_telemetry(self, msg: TelemetryMessage, sender: Target) -> None:
        """Handle incoming telemetry information."""
        self.data.telemetry_store.store(msg, sender)

        # Check if round is done
        # If so, use this as cue to start the next round.
        if not self._current_cycle_is_finished():
            return

        # Progress to next round
        self.data.current_cycle += 1
        self._broadcast_context()

    def handle_get_telemetry(self, msg: GetTelemetryMessage, sender: Target) -> None:
        """
        Handle 'get telemetry' request.
        This handle enables getting telemetry data from the server.
        """
        cycle_id = msg.cycle_id
        cycle_data = self.data.telemetry_store.aggregate(cycle_id)
        response = TelemetryMessage(-1, cycle_id, TelemetryType.AGGREGATE, cycle_data)
        self.reply(response)

    def _broadcast_context(self) -> None:
        """
        Broadcast CycleContext of current cycle to all participants.
        This starts this round
        """
        context = self._load_context(self.data.current_cycle)
        msg = ContextMessage(context)
        for peer in self.data.participants:
            MessageSender.send(msg, peer)

    def _current_cycle_is_finished(self) -> bool:
        """Returns whether the current cycle is finished."""
        current_cycle = self.data.current_cycle
        cycle_telemetry_data = self.data.telemetry_store.get(current_cycle)

        if current_cycle < 0:
            # Check if all peers submitted decrypt data
            keys = [(TelemetryType.BOOTSTRAP, ip) for ip in self.data.participants]
        else:
            # Check if all peers submitted decrypt data
            keys = [(TelemetryType.DECRYPT, ip) for ip in self.data.participants]

        all_submitted = all(lambda key: key in cycle_telemetry_data, keys)
        return all_submitted

    def _load_context(self, cycle_id: CycleID) -> CycleContext:
        """
        Load context from file.

        :param cycle_id: id of cycle to load
        :return: loaded cycle context
        """
        data: list = pickle.load(self.data.context_data_file)
        return data[cycle_id]
