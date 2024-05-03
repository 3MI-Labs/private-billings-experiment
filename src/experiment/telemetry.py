from enum import Enum
import time
from private_billing import CycleID
from private_billing.server import Target
from experiment import TelemetryMessage


class TelemetryType(Enum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    COMPUTE_BILL = "compute_bill"
    BOOTSTRAP = "bootstrap"
    AGGREGATE = "aggregate"


class TelemetryDataStore:

    def __init__(self):
        self.data = {}

    def store(self, msg: TelemetryMessage, origin: Target) -> None:
        arrival_time = time.clock()
        self.data.setdefault(msg.cycle_id, {})
        k = (msg.telemetry_type, origin)
        self.data[msg.cycle_id][k] = (arrival_time, msg)

    def aggregate(self, cycle_id: CycleID) -> list:
        data = self.data.get(cycle_id, {})
        return [k + v for k, v in data.items()]

    def get(self, cycle_id: CycleID) -> dict:
        return self.data.get(cycle_id, {})
