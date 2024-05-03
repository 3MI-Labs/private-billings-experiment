from dataclasses import dataclass
import time
from typing import Any, Callable, Tuple
from private_billing.server import Message, MessageType
from private_billing.core import CycleID, ClientID
from .telemetry import TelemetryType


class ExperimentMessageType(MessageType):
    START_BOOTSTRAP = "start_bootstrap"
    TELEMETRY = "telemetry"
    GET_TELEMETRY = "get_telemetry"


class BootStrapMessage(Message):
    """Message used to notify peers to start PRZS seed sharing sequence."""

    @property
    def type(self) -> MessageType:
        """Type of this message."""
        return ExperimentMessageType.START_BOOTSTRAP


@dataclass
class TelemetryMessage(Message):
    """Message used to send telemetry data to the server."""

    peer_id: ClientID
    cycle_id: CycleID
    telemetry_type: TelemetryType
    value: Any

    @property
    def type(self) -> MessageType:
        """Type of this message."""
        return ExperimentMessageType.TELEMETRY


@dataclass
class GetTelemetryMessage(Message):
    """Message used to send telemetry data to the server."""

    cycle_id: CycleID

    @property
    def type(self) -> MessageType:
        """Type of this message."""
        return ExperimentMessageType.GET_TELEMETRY


def speedtest(fn: Callable, *args) -> Tuple[Any, int]:
    """
    Measure the time it takes to execute a function

    :param fn: function to execute
    :param args: arguments used to call function
    :return: function result, time it took
    """
    start = time.clock()
    res = fn(args)
    end = time.clock()
    return res, end - start