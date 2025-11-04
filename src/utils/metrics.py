"""
Metrics calculation for LPG delivery route optimization
Calculates cost, time, efficiency, and performance metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta

from .config import DELIVERY


class MetricsCalculator:
    """Calculates various metrics for delivery route optimization"""

    def __init__(self):
        self.fuel_cost_per_gallon = DELIVERY.fuel_cost_per_gallon
        self.fuel_efficiency_mpg = DELIVERY.fuel_efficiency_mpg
        self.driver_hourly_cost = 25.0  # $25 per hour for driver
        self.vehicle_fixed_cost_per_day = 150.0  # $150 per day per vehicle

    def calculate_route_costs(self, solution: Dict) -> Dict:
        """
        Calculate comprehensive cost breakdown for a solution

        Args:
            solution: Solution dictionary containing routes

        Returns:
            Cost breakdown dictionary
        """
        if 'routes' not in solution:
            return {'total_cost': 0, 'fuel_cost': 0, 'driver_cost': 0, 'vehicle_cost': 0}

        total_distance_km = 0
        total_time_minutes = 0
        num_vehicles = len(solution['routes'])

        for route in solution['routes']:
            total_distance_km += route.get('total_distance', 0)
            # Estimate route time based on distance and service times
            route_time = self._estimate_route_time(route)
            total_time_minutes += route_time

        # Calculate fuel cost
        fuel_gallons = self._calculate_fuel_consumption(total_distance_km)
        fuel_cost = fuel_gallons * self.fuel_cost_per_gallon

        # Calculate driver cost (based on time)
        driver_cost = (total_time_minutes / 60) * self.driver_hourly_cost

        # Calculate vehicle cost (fixed cost per vehicle per day)
        vehicle_cost = num_vehicles * self.vehicle_fixed_cost_per_day

        total_cost = fuel_cost + driver_cost + vehicle_cost

        costs = {
            'total_cost': total_cost,
            'fuel_cost': fuel_cost,
            'driver_cost': driver_cost,
            'vehicle_cost': vehicle_cost,
            'total_distance_km': total_distance_km,
            'total_time_hours': total_time_minutes / 60,
            'num_vehicles': num_vehicles,
            'fuel_consumption_gallons': fuel_gallons,
            'cost_per_km': total_cost / total_distance_km if total_distance_km > 0 else 0,
            'cost_per_delivery': total_cost / sum(len(r.get('stops', [])) - 2 for r in solution['routes']) if solution['routes'] else 0
        }

        return costs

    def _estimate_route_time(self, route: Dict) -> float:
        """Estimate total time for a route in minutes"""
        # Base travel time (assuming average speed of 45 km/h mixed)
        distance_km = route.get('total_distance', 0)
        travel_time_minutes = (distance_km / 45) * 60

        # Service time for deliveries
        num_deliveries = len(route.get('stops', [])) - 2  # Exclude depot at start and end
        service_time_minutes = num_deliveries * 20  # Average 20 minutes per delivery

        total_time = travel_time_minutes + service_time_minutes
        return total_time

    def _calculate_fuel_consumption(self, distance_km: float) -> float:
        """Calculate fuel consumption in gallons"""
        # Convert km to miles (1 km = 0.621371 miles)
        distance_miles = distance_km * 0.621371
        fuel_gallons = distance_miles / self.fuel_efficiency_mpg
        return fuel_gallons

    def calculate_efficiency_metrics(self, solution: Dict, delivery_data: pd.DataFrame) -> Dict:
        """
        Calculate efficiency metrics for a solution

        Args:
            solution: Solution dictionary containing routes
            delivery_data: DataFrame with delivery point information

        Returns:
            Efficiency metrics dictionary
        """
        if 'routes' not in solution:
            return {}

        total_distance = sum(route.get('total_distance', 0) for route in solution['routes'])
        total_demand_served = sum(route.get('total_demand', 0) for route in solution['routes'])
        num_vehicles = len(solution['routes'])
        num_deliveries = sum(len(route.get('stops', [])) - 2 for route in solution['routes'])

        # Calculate capacity utilization
        total_capacity = num_vehicles * DELIVERY.vehicle_capacity
        capacity_utilization = (total_demand_served / total_capacity) * 100 if total_capacity > 0 else 0

        # Calculate deliveries per vehicle
        deliveries_per_vehicle = num_deliveries / num_vehicles if num_vehicles > 0 else 0

        # Calculate distance per delivery
        distance_per_delivery = total_distance / num_deliveries if num_deliveries > 0 else 0

        # Calculate demand per km
        demand_per_km = total_demand_served / total_distance if total_distance > 0 else 0

        # Calculate vehicle productivity (deliveries per hour)
        total_time_hours = sum(self._estimate_route_time(route) / 60 for route in solution['routes'])
        deliveries_per_hour = num_deliveries / total_time_hours if total_time_hours > 0 else 0

        efficiency_metrics = {
            'capacity_utilization_percent': capacity_utilization,
            'deliveries_per_vehicle': deliveries_per_vehicle,
            'distance_per_delivery_km': distance_per_delivery,
            'demand_per_km': demand_per_km,
            'deliveries_per_hour': deliveries_per_hour,
            'total_deliveries': num_deliveries,
            'total_demand_served': total_demand_served,
            'total_distance_km': total_distance,
            'num_vehicles_used': num_vehicles,
            'total_capacity': total_capacity
        }

        return efficiency_metrics

    def calculate_time_window_performance(self, solution: Dict, delivery_data: pd.DataFrame,
                                        time_matrix: np.ndarray) -> Dict:
        """
        Calculate time window performance metrics

        Args:
            solution: Solution dictionary containing routes
            delivery_data: DataFrame with delivery point information
            time_matrix: Travel time matrix between locations

        Returns:
            Time window performance metrics
        """
        if 'routes' not in solution:
            return {}

        # Simulate route execution to check time window compliance
        time_window_violations = []
        total_wait_time = 0
        total_service_time = 0

        for route in solution['routes']:
            route_analysis = self._analyze_route_time_windows(route, delivery_data, time_matrix)
            time_window_violations.extend(route_analysis['violations'])
            total_wait_time += route_analysis['wait_time']
            total_service_time += route_analysis['service_time']

        total_deliveries = sum(len(route.get('stops', [])) - 2 for route in solution['routes'])

        performance = {
            'time_window_violations': len(time_window_violations),
            'time_window_compliance_rate': (total_deliveries - len(time_window_violations)) / total_deliveries * 100 if total_deliveries > 0 else 100,
            'total_wait_time_minutes': total_wait_time,
            'average_wait_time_minutes': total_wait_time / total_deliveries if total_deliveries > 0 else 0,
            'total_service_time_minutes': total_service_time,
            'violation_details': time_window_violations
        }

        return performance

    def _analyze_route_time_windows(self, route: Dict, delivery_data: pd.DataFrame,
                                  time_matrix: np.ndarray) -> Dict:
        """Analyze time window compliance for a single route"""
        violations = []
        wait_time = 0
        service_time = 0

        if len(route.get('stops', [])) < 3:  # No actual deliveries
            return {'violations': violations, 'wait_time': wait_time, 'service_time': service_time}

        current_time = 8 * 60  # Start at 8:00 AM in minutes

        for i in range(1, len(route['stops']) - 1):  # Skip depot at start and end
            location_id = route['stops'][i]

            # Get travel time from previous location
            prev_location = route['stops'][i-1]
            travel_time = time_matrix[prev_location][location_id]

            # Update current time (travel + previous service)
            current_time += travel_time

            # Get delivery information
            delivery_info = delivery_data[delivery_data['id'] == location_id]
            if delivery_info.empty:
                continue

            # Get time window
            time_start = self._time_string_to_minutes(delivery_info['time_window_start'].iloc[0])
            time_end = self._time_string_to_minutes(delivery_info['time_window_end'].iloc[0])
            service_duration = delivery_info['service_time_minutes'].iloc[0]

            # Check if arrival is within time window
            if current_time < time_start:
                # Arrived early, need to wait
                wait_time += (time_start - current_time)
                current_time = time_start
            elif current_time > time_end:
                # Arrived late - this is a violation
                violations.append({
                    'location_id': location_id,
                    'arrival_time': current_time,
                    'time_window_end': time_end,
                    'late_by_minutes': current_time - time_end
                })

            # Add service time
            current_time += service_duration
            service_time += service_duration

        return {
            'violations': violations,
            'wait_time': wait_time,
            'service_time': service_time
        }

    def _time_string_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes since midnight"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute

    def compare_solutions(self, baseline: Dict, optimized: Dict) -> Dict:
        """
        Compare two solutions and calculate improvement metrics

        Args:
            baseline: Baseline solution
            optimized: Optimized solution

        Returns:
            Comparison metrics
        """
        baseline_costs = self.calculate_route_costs(baseline)
        optimized_costs = self.calculate_route_costs(optimized)

        # Calculate improvements
        distance_improvement = baseline_costs['total_distance_km'] - optimized_costs['total_distance_km']
        distance_improvement_percent = (distance_improvement / baseline_costs['total_distance_km']) * 100 if baseline_costs['total_distance_km'] > 0 else 0

        cost_improvement = baseline_costs['total_cost'] - optimized_costs['total_cost']
        cost_improvement_percent = (cost_improvement / baseline_costs['total_cost']) * 100 if baseline_costs['total_cost'] > 0 else 0

        time_improvement = baseline_costs['total_time_hours'] - optimized_costs['total_time_hours']
        time_improvement_percent = (time_improvement / baseline_costs['total_time_hours']) * 100 if baseline_costs['total_time_hours'] > 0 else 0

        fuel_improvement = baseline_costs['fuel_consumption_gallons'] - optimized_costs['fuel_consumption_gallons']
        fuel_improvement_percent = (fuel_improvement / baseline_costs['fuel_consumption_gallons']) * 100 if baseline_costs['fuel_consumption_gallons'] > 0 else 0

        comparison = {
            'distance_improvement_km': distance_improvement,
            'distance_improvement_percent': distance_improvement_percent,
            'cost_improvement': cost_improvement,
            'cost_improvement_percent': cost_improvement_percent,
            'time_improvement_hours': time_improvement,
            'time_improvement_percent': time_improvement_percent,
            'fuel_improvement_gallons': fuel_improvement,
            'fuel_improvement_percent': fuel_improvement_percent,
            'vehicles_reduction': baseline_costs['num_vehicles'] - optimized_costs['num_vehicles'],
            'baseline_costs': baseline_costs,
            'optimized_costs': optimized_costs
        }

        return comparison

    def generate_kpi_summary(self, solution: Dict, delivery_data: pd.DataFrame,
                           baseline_solution: Dict = None) -> Dict:
        """
        Generate comprehensive KPI summary for dashboard display

        Args:
            solution: Solution to analyze
            delivery_data: Delivery data DataFrame
            baseline_solution: Optional baseline for comparison

        Returns:
            KPI summary dictionary
        """
        costs = self.calculate_route_costs(solution)
        efficiency = self.calculate_efficiency_metrics(solution, delivery_data)

        kpis = {
            'cost_metrics': {
                'total_cost': costs['total_cost'],
                'fuel_cost': costs['fuel_cost'],
                'driver_cost': costs['driver_cost'],
                'vehicle_cost': costs['vehicle_cost'],
                'cost_per_km': costs['cost_per_km'],
                'cost_per_delivery': costs['cost_per_delivery']
            },
            'operational_metrics': {
                'total_distance_km': costs['total_distance_km'],
                'total_time_hours': costs['total_time_hours'],
                'num_vehicles': costs['num_vehicles'],
                'total_deliveries': efficiency.get('total_deliveries', 0),
                'total_demand_served': efficiency.get('total_demand_served', 0)
            },
            'efficiency_metrics': {
                'capacity_utilization_percent': efficiency.get('capacity_utilization_percent', 0),
                'deliveries_per_vehicle': efficiency.get('deliveries_per_vehicle', 0),
                'distance_per_delivery_km': efficiency.get('distance_per_delivery_km', 0),
                'deliveries_per_hour': efficiency.get('deliveries_per_hour', 0)
            },
            'environmental_metrics': {
                'fuel_consumption_gallons': costs['fuel_consumption_gallons'],
                'co2_emissions_lb': costs['fuel_consumption_gallons'] * 19.6,  # ~19.6 lb CO2 per gallon gasoline
                'distance_reduction_vs_baseline': 0,
                'fuel_reduction_vs_baseline': 0
            }
        }

        # Add baseline comparison if available
        if baseline_solution:
            comparison = self.compare_solutions(baseline_solution, solution)
            kpis['improvement_metrics'] = {
                'distance_reduction_percent': comparison['distance_improvement_percent'],
                'cost_reduction_percent': comparison['cost_improvement_percent'],
                'time_reduction_percent': comparison['time_improvement_percent'],
                'fuel_reduction_percent': comparison['fuel_improvement_percent'],
                'vehicles_reduction': comparison['vehicles_reduction']
            }

            # Update environmental metrics with baseline comparison
            kpis['environmental_metrics']['distance_reduction_vs_baseline'] = comparison['distance_improvement_km']
            kpis['environmental_metrics']['fuel_reduction_vs_baseline'] = comparison['fuel_improvement_gallons']

        return kpis


def main():
    """Test function for metrics calculation"""
    # Create test solution
    test_solution = {
        'routes': [
            {
                'stops': [0, 1, 2, 3, 0],
                'total_distance': 45.2,
                'total_demand': 35
            },
            {
                'stops': [0, 4, 5, 0],
                'total_distance': 28.7,
                'total_demand': 25
            }
        ]
    }

    # Create test delivery data
    delivery_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'demand': [10, 15, 10, 12, 13],
        'time_window_start': ['08:00', '09:00', '10:00', '11:00', '12:00'],
        'time_window_end': ['10:00', '11:00', '12:00', '13:00', '14:00'],
        'service_time_minutes': [20, 25, 20, 22, 23]
    })

    # Calculate metrics
    calculator = MetricsCalculator()

    costs = calculator.calculate_route_costs(test_solution)
    print("Cost Metrics:")
    for key, value in costs.items():
        print(f"  {key}: {value}")

    efficiency = calculator.calculate_efficiency_metrics(test_solution, delivery_data)
    print("\nEfficiency Metrics:")
    for key, value in efficiency.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()