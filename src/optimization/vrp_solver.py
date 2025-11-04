"""
Vehicle Routing Problem (VRP) solver using Google OR-Tools
Handles capacity constraints, time windows, and route optimization
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
import time
from datetime import datetime, timedelta

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from ..utils.config import (
    DELIVERY, OPTIMIZATION, GEOGRAPHIC,
    get_output_path
)


class VRPSolver:
    """Vehicle Routing Problem solver using Google OR-Tools"""

    def __init__(self, delivery_data: pd.DataFrame, distance_matrix: np.ndarray,
                 time_matrix: np.ndarray):
        self.delivery_data = delivery_data
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix
        self.num_locations = len(delivery_data)

        # Extract demands (excluding depot)
        self.demands = [0] + delivery_data[delivery_data['id'] != 0]['demand'].tolist()

        # Solution storage
        self.solution = None
        self.routes = None
        self.objective_value = None
        self.solver_time = 0

    def _create_data_model(self, num_vehicles: int = None) -> Dict:
        """Create the data model for OR-Tools"""
        if num_vehicles is None:
            num_vehicles = min(OPTIMIZATION.max_vehicles,
                             max(3, self.num_locations // 5))  # At least 3 vehicles

        data = {
            'distance_matrix': self.distance_matrix.tolist(),
            'time_matrix': self.time_matrix.tolist(),
            'demands': self.demands,
            'vehicle_capacities': [DELIVERY.vehicle_capacity] * num_vehicles,
            'num_vehicles': num_vehicles,
            'depot': 0  # Depot is always location 0
        }

        return data

    def _create_time_windows(self) -> List[Tuple[int, int]]:
        """Create time windows for all locations in minutes since start of day"""
        time_windows = []

        for _, row in self.delivery_data.iterrows():
            start_time = row['time_window_start']
            end_time = row['time_window_end']

            # Parse time strings to minutes since midnight
            start_minutes = self._time_to_minutes(start_time)
            end_minutes = self._time_to_minutes(end_time)

            time_windows.append((start_minutes, end_minutes))

        return time_windows

    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes since midnight"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute

    def _minutes_to_time_str(self, minutes: int) -> str:
        """Convert minutes since midnight to time string"""
        hour = minutes // 60
        minute = minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def _print_solution(self, data, manager, routing, solution):
        """Print solution on console."""
        print(f'Objective: {solution.ObjectiveValue()}')
        max_route_distance = 0
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = f'Route for vehicle {vehicle_id}:\n'
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                plan_output += f' {node_index} ->'
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            plan_output += f' {manager.IndexToNode(index)}\n'
            plan_output += f'Distance of the route: {route_distance}m\n'
            print(plan_output)
            max_route_distance = max(route_distance, max_route_distance)
        print(f'Maximum of the route distances: {max_route_distance}m')

    def solve_vrp(self, num_vehicles: int = None, time_limit_seconds: int = None,
                  include_time_windows: bool = True) -> Dict[str, Any]:
        """
        Solve the Vehicle Routing Problem

        Args:
            num_vehicles: Number of vehicles to use
            time_limit_seconds: Time limit for solver
            include_time_windows: Whether to include time window constraints

        Returns:
            Dictionary containing solution details
        """
        start_time = time.time()

        # Create data model
        data = self._create_data_model(num_vehicles)

        # Create the routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot'])

        # Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity constraint
        def demand_callback(from_index):
            """Returns the demand of the node."""
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

        # Add Time Window constraint if requested
        if include_time_windows:
            time_windows = self._create_time_windows()

            def time_callback(from_index, to_index):
                """Returns the travel time between the two nodes."""
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return data['time_matrix'][from_node][to_node]

            time_callback_index = routing.RegisterTransitCallback(time_callback)

            # Add time dimension
            routing.AddDimension(
                time_callback_index,
                30,  # allow waiting time
                DELIVERY.max_route_duration_hours * 60,  # maximum time per vehicle
                False,  # Don't force start cumul to zero
                'Time')

            time_dimension = routing.GetDimensionOrDie('Time')

            # Add time window constraints for each location except depot
            for location_idx, time_window in enumerate(time_windows):
                if location_idx == 0:  # Skip depot
                    continue
                index = manager.NodeToIndex(location_idx)
                time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

            # Add time window constraints for depot start and end
            depot_idx = 0
            for vehicle_id in range(data['num_vehicles']):
                index = routing.Start(vehicle_id)
                time_dimension.CumulVar(index).SetRange(
                    time_windows[depot_idx][0],
                    time_windows[depot_idx][1])

        # Setting first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        # Set first solution strategy
        if OPTIMIZATION.first_solution_strategy == "PATH_CHEAPEST_ARC":
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Set local search metaheuristic
        if OPTIMIZATION.local_search_metaheuristic == "GUIDED_LOCAL_SEARCH":
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

        # Set time limit
        time_limit = time_limit_seconds or OPTIMIZATION.solver_time_limit_seconds
        search_parameters.time_limit.FromSeconds(time_limit)

        # Solve the problem
        print(f"Starting VRP solver with {data['num_vehicles']} vehicles...")
        print(f"Time limit: {time_limit} seconds")

        solution = routing.SolveWithParameters(search_parameters)

        # Calculate solver time
        self.solver_time = time.time() - start_time

        # Process solution
        if solution:
            print(f'Solution found in {self.solver_time:.2f} seconds!')
            self.solution = solution
            self.objective_value = solution.ObjectiveValue()
            self.routes = self._extract_routes(data, manager, routing, solution)

            return self._create_solution_dict(data, manager, routing, solution)
        else:
            print('No solution found!')
            return {'status': 'no_solution', 'solver_time': self.solver_time}

    def _extract_routes(self, data, manager, routing, solution) -> List[Dict]:
        """Extract routes from solution"""
        routes = []

        for vehicle_id in range(data['num_vehicles']):
            route = {
                'vehicle_id': vehicle_id,
                'stops': [],
                'total_distance': 0,
                'total_demand': 0,
                'total_time': 0
            }

            index = routing.Start(vehicle_id)
            route_distance = 0
            route_demand = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route['stops'].append(node_index)

                if node_index != 0:  # Not depot
                    route_demand += data['demands'][node_index]

                previous_index = index
                index = solution.Value(routing.NextVar(index))

                if not routing.IsEnd(index):
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id)

            # Add final return to depot
            if len(route['stops']) > 1:  # Only if vehicle actually made deliveries
                route['total_distance'] = route_distance
                route['total_demand'] = route_demand
                route['stops'].append(0)  # Return to depot
                routes.append(route)

        return routes

    def _create_solution_dict(self, data, manager, routing, solution) -> Dict:
        """Create comprehensive solution dictionary"""
        solution_dict = {
            'status': 'optimal',
            'objective_value': self.objective_value,
            'solver_time_seconds': self.solver_time,
            'num_vehicles_used': len([r for r in self.routes if r['stops']]),
            'total_distance': sum(r['total_distance'] for r in self.routes),
            'total_demand_served': sum(r['total_demand'] for r in self.routes),
            'routes': self.routes,
            'unassigned_customers': [],
            'statistics': self._calculate_solution_statistics()
        }

        return solution_dict

    def _calculate_solution_statistics(self) -> Dict:
        """Calculate detailed statistics about the solution"""
        if not self.routes:
            return {}

        route_distances = [r['total_distance'] for r in self.routes if r['stops']]
        route_demands = [r['total_demand'] for r in self.routes if r['stops']]
        route_stops = [len(r['stops']) - 2 for r in self.routes if r['stops']]  # Exclude depot returns

        stats = {
            'vehicles_used': len(self.routes),
            'total_distance_km': sum(route_distances),
            'average_distance_per_route': sum(route_distances) / len(route_distances) if route_distances else 0,
            'max_distance_route': max(route_distances) if route_distances else 0,
            'min_distance_route': min(route_distances) if route_distances else 0,
            'total_deliveries': sum(route_stops),
            'average_deliveries_per_route': sum(route_stops) / len(route_stops) if route_stops else 0,
            'total_demand_served': sum(route_demands),
            'average_demand_per_route': sum(route_demands) / len(route_demands) if route_demands else 0,
            'route_utilization_percent': sum(route_demands) / (len(self.routes) * DELIVERY.vehicle_capacity) * 100
        }

        return stats

    def create_baseline_solution(self) -> Dict:
        """Create a simple greedy baseline solution for comparison"""
        print("Creating baseline solution using greedy nearest neighbor...")

        # Simple nearest neighbor from depot
        unvisited = set(range(1, self.num_locations))  # Exclude depot
        routes = []
        vehicle_id = 0

        while unvisited:
            route = {
                'vehicle_id': vehicle_id,
                'stops': [0],  # Start at depot
                'total_distance': 0,
                'total_demand': 0
            }

            current = 0  # Start at depot
            current_capacity = 0

            while unvisited and current_capacity < DELIVERY.vehicle_capacity * 0.9:
                # Find nearest unvisited location
                nearest = None
                nearest_distance = float('inf')

                for location in unvisited:
                    distance = self.distance_matrix[current][location]
                    if distance < nearest_distance:
                        nearest = location
                        nearest_distance = distance

                if nearest is None:
                    break

                # Check capacity constraint
                demand = self.demands[nearest]
                if current_capacity + demand > DELIVERY.vehicle_capacity:
                    break

                # Add to route
                route['stops'].append(nearest)
                route['total_distance'] += nearest_distance
                route['total_demand'] += demand
                current_capacity += demand

                unvisited.remove(nearest)
                current = nearest

            # Return to depot
            if len(route['stops']) > 1:
                return_distance = self.distance_matrix[current][0]
                route['stops'].append(0)
                route['total_distance'] += return_distance
                routes.append(route)
                vehicle_id += 1

        baseline_stats = {
            'total_distance': sum(r['total_distance'] for r in routes),
            'total_demand_served': sum(r['total_demand'] for r in routes),
            'num_vehicles_used': len(routes),
            'routes': routes
        }

        return baseline_stats

    def save_solution(self, filename: str = None) -> str:
        """Save solution to JSON file"""
        import json

        if filename is None:
            timestamp = int(time.time())
            filename = f"vrp_solution_{timestamp}.json"

        filepath = get_output_path(filename)

        solution_data = {
            'objective_value': self.objective_value,
            'solver_time_seconds': self.solver_time,
            'routes': self.routes,
            'statistics': self._calculate_solution_statistics(),
            'timestamp': datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(solution_data, f, indent=2)

        return filepath


def main():
    """Test function for VRP solver"""
    from ..data.mock_data_generator import MockDataGenerator
    from ..data.distance_matrix import DistanceMatrix

    # Generate test data
    generator = MockDataGenerator(seed=42)
    delivery_data = generator.generate_delivery_data(num_deliveries=15)

    # Create distance matrix
    distance_calc = DistanceMatrix(delivery_data)
    distance_matrix, time_matrix = distance_calc.get_matrices()

    # Solve VRP
    solver = VRPSolver(delivery_data, distance_matrix, time_matrix)
    solution = solver.solve_vrp()

    print("\nSolution Summary:")
    print(f"Status: {solution['status']}")
    print(f"Total Distance: {solution['total_distance']:.2f} km")
    print(f"Vehicles Used: {solution['num_vehicles_used']}")
    print(f"Solver Time: {solution['solver_time_seconds']:.2f} seconds")

    # Compare with baseline
    baseline = solver.create_baseline_solution()
    print(f"\nBaseline Distance: {baseline['total_distance']:.2f} km")
    print(f"Optimization Improvement: {(baseline['total_distance'] - solution['total_distance']):.2f} km")


if __name__ == "__main__":
    main()