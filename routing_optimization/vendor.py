from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
from yaml import safe_load


class Vendor(Enum):
    VENDOR_01 = "vendor_1"
    VENDOR_02 = "vendor_2"
    VENDOR_03 = "vendor_3"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


@dataclass
class VendorData:
    vendor: Vendor
    minimum_volume: int = None
    maximum_volume: int = None
    price_tiers: List[Dict]

    def has_minimum_volume(self):
        return self.minimum_volume is not None

    def has_maximum_volume(self):
        return self.minimum_volume is not None

    @staticmethod
    def load_vendors_from_config(config_file_path: str):
        """ """
        vendor_list = []

        with open(config_file_path, "r") as f:
            vendor_data = safe_load(f)

        for vendor_name, data in vendor_data.items():
            vendor = Vendor.from_value(vendor_name)

            vendor_data = VendorData(
                vendor=vendor,
                minimum_volume=getattr(data["minimum_volume"], None),
                maximum_volume=getattr(data["maximum_volume"], None),
                price_tiers=getattr(data["price_tiers"], None),
            )
            vendor_list.append(vendor_data)

        return vendor_list
