from enum import Enum
from yaml import safe_load
from typing import List, Dict

from routing_optimization.vendor import Vendor


class PacketType(Enum):
    PACKET_TYPE_001 = "packet_type_1"
    PACKET_TYPE_002 = "packet_type_2"
    PACKET_TYPE_003 = "packet_type_3"
    PACKET_TYPE_004 = "packet_type_4"
    PACKET_TYPE_005 = "packet_type_5"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


def load_packet_vendors_from_config(config_file_path: str) -> Dict[PacketType, List[Vendor]]:
    with open(config_file_path, 'r') as f:
        packet_type_data = safe_load(f)
    
    packet_vendors = dict()
    for packet_name, allowed_vendors  in packet_type_data.items():
        packet_vendors[PacketType.from_value(packet_name)] = [Vendor.from_value(vendor) for vendor in allowed_vendors]
    
    return packet_vendors
