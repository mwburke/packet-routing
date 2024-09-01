from dataclasses import dataclass
from typing import Dict, List

from ortools.linear_solver import pywraplp

from routing_optimization.vendor import VendorData, Vendor
from routing_optimization.packet import Packet


@dataclass
class VendorTarget:
    volume: int
    min_volume: int
    cost_per_packet: float


class PriceTierOptimizer:
    @staticmethod
    def calculate_optimal_price_tiers(
        packet_volume: Dict[Packet, float], vendors: List[VendorData]
    ) -> Dict[Vendor, VendorTarget]:
        """
        Given a total volume of packets, determine the optimal way to
        distribute them among vendors to minimize cost.

        Args:
            total_volume : int
                Total number of packets to be shipped
            vendors : List[VendorData]
                List of vendor information regarding volume constraints
                and price tiers
        """
        total_volume = sum([v] for v in packet_volume.values())

        # Create the solver
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            return None

        # Decision variables:
        # Number of packets to ship with each vendor at each tier
        x = []
        for vendor in vendors:
            vendor_tiers = []
            for j in range(len(vendor.price_tiers)):
                vendor_tiers.append(
                    solver.IntVar(
                        0,
                        solver.infinity(),
                        f"x_{i}_{j}_{vendor.vendor.value}",
                    )
                )
            x.append(vendor_tiers)

        # Objective function: minimize total cost
        total_cost = solver.Sum(
            vendors[i].price_tiers[j]["cost_per_packet"] * x[i][j]
            for i in range(len(vendors))
            for j in range(len(vendors[i]["tiers"]))
        )
        solver.Minimize(total_cost)

        # Constraint: total number of packets to ship
        total_packets = solver.Sum(
            x[i][j]
            for i in range(len(vendors))
            for j in range(len(vendors[i].price_tiers))
        )
        solver.Add(total_packets == total_volume)

        # Constraints: minimum and maximum packets for each vendor
        for i in range(len(vendors)):
            vendor_packets = solver.Sum(
                x[i][j] for j in range(len(vendors[i].price_tiers))
            )
            if vendors[i].has_minimum_volume():
                solver.Add(vendor_packets >= vendors[i].min_packets)
            if vendors[i].has_maximum_volume():
                solver.Add(vendor_packets <= vendors[i].max_packets)

            # Ensure that packets are assigned to tiers in the correct order
            for j in range(1, len(vendors[i].price_tiers)):
                min_volume_for_prev_tier = vendors[i].price_tiers[j - 1][
                    "minimum_volume"
                ]
                solver.Add(vendor_packets >= min_volume_for_prev_tier)

        # Solve the problem
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            vendor_volume = dict()
            print("Solution:")
            for i in range(vendors):
                print(f"Vendor {i}:")
                vendor_sum = 0
                for j in range(len(vendors[i].price_tiers)):
                    vendor_sum += x[i][j].solution_value()
                    print(f"  Tier {j}: {x[i][j].solution_value()} packets")
                vendor_volume[vendors[i].vendor] = VendorTarget(
                    volume=vendor_sum,
                    minimum_volume=vendors[i].price_tiers[j]["minimum_volume"],
                    cost_per_packet=vendors[i].price_tiers[j][
                        "cost_per_packet"
                    ],
                )
            print("Total cost =", solver.Objective().Value())
        else:
            print("The problem does not have an optimal solution.")

        return vendor_volume
