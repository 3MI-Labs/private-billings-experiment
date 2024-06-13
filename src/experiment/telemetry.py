from enum import Enum
import time
from dataclasses import dataclass
from typing import Any
from private_billing import CycleID
from private_billing.network import NodeInfo
from private_billing.server import MessageType, Message
from private_billing.core import ClientID
from .experiment import ExperimentMessageType


class TelemetryType(Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    COMPUTE_BILL = "compute_bill"
    BOOTSTRAP = "bootstrap"
    AGGREGATE = "aggregate"


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


class TelemetryDataStore:

    def __init__(self):
        self.data = {}

    def store(self, msg: TelemetryMessage, origin: NodeInfo) -> None:
        arrival_time = time.time()
        self.data.setdefault(msg.cycle_id, {})
        k = (msg.telemetry_type, origin.id)
        self.data[msg.cycle_id][k] = (arrival_time, msg)

    def aggregate(self, cycle_id: CycleID) -> list:
        data = self.data.get(cycle_id, {})
        return [k + v for k, v in data.items()]

    def get(self, cycle_id: CycleID) -> dict:
        return self.data.get(cycle_id, {})
