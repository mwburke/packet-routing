from dataclasses import dataclass
from typing import Dict, List, Optional

from routing_optimization.vendor import Vendor
from routing_optimization.packet import PacketType


class PacketRouter:
    def __init__(
        self, payment_vendor_routes: Dict[PacketType, Dict[Vendor, float]]
    ) -> None:
        for packet_type, vendor_fractions in payment_vendor_routes.items():
            total_fraction = sum(vendor_fractions.values())
            if total_fraction != 1:
                raise ValueError(
                    f"Fractions for {packet_type} do not sum to 1"
                )

        payment_vendor_routers = dict()
        for packet_type, vendor_fractions in payment_vendor_routes.items():
            payment_vendor_routers[packet_type] = VendorRouter(
                vendor_fractions
            )

        self.payment_vendor_routers = payment_vendor_routers

    def get_vendor(self, packet_type: PacketType, fraction: float) -> Vendor:
        return self.payment_vendor_routers[packet_type].get_vendor(fraction)


@dataclass
class VendorRouter:
    vendor_fractions: Dict[Vendor, float]
    cumulative_fractions: Optional[List[float]] = None
    cumulative_vendors: Optional[List[Vendor]] = None

    def __post_init__(self) -> None:
        self._prepare_cumulative_fractions()

    def _prepare_cumulative_fractions(self) -> None:
        cumulative_fractions = []
        cumulative_vendors = []
        fraction = 0
        for vendor, v_fraction in self.vendor_fractions.items():
            fraction += v_fraction
            cumulative_fractions.append(fraction)
            cumulative_vendors.append(vendor)

        self.cumulative_fractions = cumulative_fractions
        self.cumulative_vendors = cumulative_vendors

    def get_vendor(self, fraction: float) -> Vendor:
        if not self.cumulative_fractions:
            self._prepare_cumulative_fractions()

        for i, cum_fraction in enumerate(self.cumulative_fractions):
            if fraction <= cum_fraction:
                return self.cumulative_vendors[i]

        # Default to last
        return self.cumulative_vendors[-1]
