from private_billing import BillingServer
from private_billing.core import CycleID
from private_billing.messages import BillMessage
from private_billing.server import MessageSender

from .experiment import speedtest
from .telemetry import TelemetryType, TelemetryMessage


class ExperimentServer(BillingServer):

    def run_billing(self, cycle_id: CycleID) -> None:
        bills, time = speedtest(self.data.shared_biller.compute_bills, cycle_id)

        # Send bills to each participant
        for peer_id, bill in bills.items():
            peer = self.data.participants[peer_id]
            msg = BillMessage(bill)
            MessageSender.send(msg, peer)

        # Send telemetry data
        telemetry_msg = TelemetryMessage(
            self.id, cycle_id, TelemetryType.COMPUTE_BILL, time
        )
        MessageSender.send(telemetry_msg, self.data.market_operator)
