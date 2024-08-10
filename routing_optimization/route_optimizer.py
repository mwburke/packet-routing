from typing import Dict, List

from ortools.linear_solver import pywraplp

from routing_optimization.vendor import Vendor
from routing_optimization.packet import PacketType
from routing_optimization.price_optimizer import VendorTarget


class PacketRouteOptimizer:
    @staticmethod
    def calculate_packet_vendor_routing(
        packet_volume: Dict[PacketType, float],
        vendor_data: Dict[Vendor, VendorTarget],
        packet_vendors: Dict[PacketType, List[Vendor]]
    ) -> Dict[PacketType, Dict[Vendor, float]]:
        """
        Given a total volume of packets, determine the optimal way to
        distribute them among vendors to minimize cost. They are routed
        using a fractional mapping of each payment type to each vendor
        that accepts that type of packet.

        Args:
            packet_volume : Dict[PacketType, float]
                Total number of packets to be shipped
            vendor_data : Dict[Vendor, VendorTarget]
                List of vendor information regarding volume constraints
                and price tiers
            packet_vendors : Dict[PacketType, List[Vendor]]
                List of vendors that accept each packet type
        """
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            return None

        # There should be some volume to each relevant vendor guaranteed
        vendors = [v for v in packet_vendors.keys()]
        num_vendors = len(vendors)
        packet_types = [p for p in packet_volume.keys()]
        num_packet_types = len(packet_types)

        # Decision variables: fraction of each package type to ship with each vendor
        x = []
        for i, packet_type in enumerate(packet_types):
            package_vendors = []
            for j, vendor in enumerate(vendors):
                if vendor in packet_vendors[packet_type]:
                    package_vendors.append(solver.NumVar(0, 1, f"x_{i}_{j}"))
                else:
                    package_vendors.append(
                        solver.NumVar(0, 0, f"x_{i}_{j}")
                    )  # Not allowed
            x.append(package_vendors)

        # Objective function: minimize total cost
        total_cost = solver.Sum(
            packet_volume[packet_type] * vendor_data[vendor].cost_per_packet * x[i][j]
            for i, packet_type in enumerate(packet_types)
            for j, vendor in enumerate(vendors)
        )
        solver.Minimize(total_cost)

        # Constraint: each package type must be fully shipped
        for i in range(num_packet_types):
            solver.Add(solver.Sum(x[i][j] for j in range(num_vendors)) == 1)

        # Constraint: total packages shipped by each vendor must meet minimum requirements
        for j, vendor in enumerate(vendors):
            total_shipped_by_vendor = solver.Sum(
                packet_volume[packet_type] * x[i][j] for i, packet_type in enumerate(packet_types)
            )
            if "min_packages" in vendors[j]:
                solver.Add(total_shipped_by_vendor >= vendors[j]["min_packages"])

        # Solve the problem
        status = solver.Solve()

        packet_vendor_routes = dict()
        if status == pywraplp.Solver.OPTIMAL:
            print("Solution:")
            for i, packet_type in enumerate(packet_types):
                print(f"Package Type {i}:")
                for j, vendor in enumerate(vendors):
                    if x[i][j].solution_value() > 0:
                        print(f"  Vendor {j}: {x[i][j].solution_value() * 100:.2f}%")
                        if packet_type not in packet_vendor_routes:
                            packet_vendor_routes[packet_type] = dict()
                        packet_vendor_routes[packet_type][vendor] = x[i][j].solution_value()
            print("Total cost =", solver.Objective().Value())
        else:
            print("The problem does not have an optimal solution.")

        return packet_vendor_routes
