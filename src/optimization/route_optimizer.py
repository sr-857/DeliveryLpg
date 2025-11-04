"""
Main route optimization coordinator
Orchestrates the complete optimization workflow from data to solution
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Any
import time
from datetime import datetime

from ..data.mock_data_generator import MockDataGenerator
from ..data.distance_matrix import DistanceMatrix
from ..vrp_solver import VRPSolver
from ..utils.config import (
    DATA_GENERATION, OPTIMIZATION, DELIVERY,
    get_output_path
)


class RouteOptimizer:
    """Main coordinator for route optimization workflow"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.delivery_data = None
        self.distance_matrix = None
        self.time_matrix = None
        self.baseline_solution = None
        self.optimized_solution = None
        self.optimization_time = 0

    def generate_delivery_scenario(self, num_deliveries: int = None,
                                 save_data: bool = True) -> Tuple[pd.DataFrame, Dict]:
        """
        Generate a new delivery scenario

        Args:
            num_deliveries: Number of delivery points to generate
            save_data: Whether to save the generated data

        Returns:
            Tuple of (delivery_data_df, scenario_summary)
        """
        print(f"Generating delivery scenario with {num_deliveries or DATA_GENERATION.default_deliveries} deliveries...")

        # Generate data
        generator = MockDataGenerator(seed=self.seed)
        delivery_data = generator.generate_delivery_data(num_deliveries)

        # Create summary
        summary = generator.generate_scenario_summary(delivery_data)

        # Save data if requested
        if save_data:
            timestamp = int(time.time())
            filename = f"delivery_scenario_{timestamp}.csv"
            filepath = generator.save_delivery_data(delivery_data, filename)
            summary['data_file'] = filepath

        self.delivery_data = delivery_data
        return delivery_data, summary

    def calculate_distance_matrices(self, save_matrices: bool = True) -> Dict:
        """
        Calculate distance and time matrices

        Args:
            save_matrices: Whether to save the matrices to files

        Returns:
            Dictionary with matrix statistics
        """
        if self.delivery_data is None:
            raise ValueError("Delivery data must be generated first")

        print("Calculating distance and time matrices...")

        # Create distance calculator
        distance_calc = DistanceMatrix(self.delivery_data)

        # Compute matrices
        start_time = time.time()
        self.distance_matrix = distance_calc.compute_distance_matrix()
        self.time_matrix = distance_calc.compute_time_matrix()
        matrix_time = time.time() - start_time

        # Get statistics
        stats = distance_calc.get_matrix_statistics()
        stats['matrix_calculation_time_seconds'] = matrix_time

        # Save matrices if requested
        if save_matrices:
            matrix_files = distance_calc.save_matrices()
            stats['matrix_files'] = matrix_files

        return stats

    def run_optimization(self, num_vehicles: int = None,
                        include_time_windows: bool = True,
                        time_limit_seconds: int = None,
                        create_baseline: bool = True) -> Dict:
        """
        Run complete route optimization

        Args:
            num_vehicles: Number of vehicles to use
            include_time_windows: Whether to include time window constraints
            time_limit_seconds: Solver time limit
            create_baseline: Whether to create baseline solution for comparison

        Returns:
            Optimization results dictionary
        """
        if self.delivery_data is None or self.distance_matrix is None:
            raise ValueError("Delivery data and distance matrices must be calculated first")

        print("Starting route optimization...")
        start_time = time.time()

        # Create VRP solver
        solver = VRPSolver(self.delivery_data, self.distance_matrix, self.time_matrix)

        # Run optimization
        self.optimized_solution = solver.solve_vrp(
            num_vehicles=num_vehicles,
            time_limit_seconds=time_limit_seconds,
            include_time_windows=include_time_windows
        )

        # Create baseline if requested
        if create_baseline:
            print("Creating baseline solution for comparison...")
            self.baseline_solution = solver.create_baseline_solution()
        else:
            self.baseline_solution = None

        self.optimization_time = time.time() - start_time

        # Create comprehensive results
        results = self._create_optimization_results()

        # Save results
        self._save_optimization_results(results)

        return results

    def _create_optimization_results(self) -> Dict:
        """Create comprehensive optimization results"""
        results = {
            'optimization_info': {
                'timestamp': datetime.now().isoformat(),
                'total_optimization_time_seconds': self.optimization_time,
                'num_deliveries': len(self.delivery_data) - 1,  # Exclude depot
                'solver_status': self.optimized_solution['status'],
                'seed': self.seed
            },
            'optimized_solution': self.optimized_solution,
            'scenario_statistics': self._get_scenario_statistics()
        }

        # Add baseline comparison if available
        if self.baseline_solution:
            results['baseline_solution'] = self.baseline_solution
            results['improvement_metrics'] = self._calculate_improvement_metrics()

        return results

    def _get_scenario_statistics(self) -> Dict:
        """Get statistics about the current scenario"""
        if self.delivery_data is None:
            return {}

        # Exclude depot from statistics
        delivery_df = self.delivery_data[self.delivery_data['id'] != 0]

        stats = {
            'total_deliveries': len(delivery_df),
            'total_demand': int(delivery_df['demand'].sum()),
            'urban_deliveries': int((delivery_df['area_type'] == 'urban').sum()),
            'rural_deliveries': int((delivery_df['area_type'] == 'rural').sum()),
            'priority_distribution': delivery_df['priority'].value_counts().to_dict(),
            'depot_location': {
                'latitude': float(self.delivery_data[self.delivery_data['id'] == 0]['latitude'].iloc[0]),
                'longitude': float(self.delivery_data[self.delivery_data['id'] == 0]['longitude'].iloc[0])
            }
        }

        # Time window statistics
        delivery_df['time_window_start_minutes'] = delivery_df['time_window_start'].apply(
            lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])
        )
        stats['time_window_stats'] = {
            'earliest_start': int(delivery_df['time_window_start_minutes'].min()),
            'latest_start': int(delivery_df['time_window_start_minutes'].max()),
            'average_window_duration': DATA_GENERATION.time_window_duration_hours * 60
        }

        return stats

    def _calculate_improvement_metrics(self) -> Dict:
        """Calculate improvement metrics compared to baseline"""
        if not self.baseline_solution or not self.optimized_solution:
            return {}

        baseline_distance = self.baseline_solution['total_distance']
        optimized_distance = self.optimized_solution['total_distance']
        baseline_vehicles = self.baseline_solution['num_vehicles_used']
        optimized_vehicles = self.optimized_solution['num_vehicles_used']

        distance_reduction = baseline_distance - optimized_distance
        distance_reduction_percent = (distance_reduction / baseline_distance) * 100 if baseline_distance > 0 else 0

        vehicle_reduction = baseline_vehicles - optimized_vehicles
        vehicle_reduction_percent = (vehicle_reduction / baseline_vehicles) * 100 if baseline_vehicles > 0 else 0

        # Calculate cost savings
        from ..utils.metrics import MetricsCalculator
        calculator = MetricsCalculator()

        baseline_costs = calculator.calculate_route_costs(self.baseline_solution)
        optimized_costs = calculator.calculate_route_costs(self.optimized_solution)

        cost_savings = baseline_costs['total_cost'] - optimized_costs['total_cost']
        cost_savings_percent = (cost_savings / baseline_costs['total_cost']) * 100 if baseline_costs['total_cost'] > 0 else 0

        improvements = {
            'distance_reduction_km': distance_reduction,
            'distance_reduction_percent': distance_reduction_percent,
            'vehicle_reduction': vehicle_reduction,
            'vehicle_reduction_percent': vehicle_reduction_percent,
            'cost_savings': cost_savings,
            'cost_savings_percent': cost_savings_percent,
            'baseline': {
                'total_distance_km': baseline_distance,
                'vehicles_used': baseline_vehicles,
                'total_cost': baseline_costs['total_cost']
            },
            'optimized': {
                'total_distance_km': optimized_distance,
                'vehicles_used': optimized_vehicles,
                'total_cost': optimized_costs['total_cost']
            }
        }

        return improvements

    def _save_optimization_results(self, results: Dict) -> None:
        """Save optimization results to file"""
        import json

        timestamp = int(time.time())
        filename = f"optimization_results_{timestamp}.json"
        filepath = get_output_path(filename)

        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj

        serializable_results = convert_numpy_types(results)

        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=2)

        results['results_file'] = filepath

    def optimize_single_scenario(self, num_deliveries: int = None,
                               num_vehicles: int = None,
                               **kwargs) -> Dict:
        """
        Run complete optimization workflow for a single scenario

        Args:
            num_deliveries: Number of deliveries to generate
            num_vehicles: Number of vehicles to use
            **kwargs: Additional arguments for optimization

        Returns:
            Complete optimization results
        """
        print("=" * 60)
        print("LPG DELIVERY ROUTE OPTIMIZATION")
        print("=" * 60)

        # Step 1: Generate delivery scenario
        delivery_data, scenario_summary = self.generate_delivery_scenario(num_deliveries)
        print(f"✓ Generated {scenario_summary['total_deliveries']} deliveries")
        print(f"  - Urban: {scenario_summary['urban_deliveries']}, Rural: {scenario_summary['rural_deliveries']}")
        print(f"  - Total demand: {scenario_summary['total_demand']} LPG cylinders")

        # Step 2: Calculate distance matrices
        matrix_stats = self.calculate_distance_matrices()
        print(f"✓ Calculated distance and time matrices in {matrix_stats['matrix_calculation_time_seconds']:.2f}s")
        print(f"  - Average distance: {matrix_stats['distance_stats']['mean_km']:.1f} km")
        print(f"  - Average travel time: {matrix_stats['time_stats']['mean_minutes']:.1f} min")

        # Step 3: Run optimization
        results = self.run_optimization(num_vehicles=num_vehicles, **kwargs)
        print(f"✓ Optimization completed in {self.optimization_time:.2f}s")

        # Print results summary
        self._print_optimization_summary(results)

        return results

    def _print_optimization_summary(self, results: Dict) -> None:
        """Print optimization results summary"""
        optimized = results['optimized_solution']

        print("\n" + "=" * 40)
        print("OPTIMIZATION RESULTS")
        print("=" * 40)

        if optimized['status'] == 'no_solution':
            print("❌ No feasible solution found")
            return

        print(f"Status: {optimized['status']}")
        print(f"Total Distance: {optimized['total_distance']:.2f} km")
        print(f"Vehicles Used: {optimized['num_vehicles_used']}")
        print(f"Total Demand Served: {optimized['total_demand_served']} cylinders")

        # Print improvement metrics if available
        if 'improvement_metrics' in results:
            improvements = results['improvement_metrics']
            print(f"\n📊 IMPROVEMENTS vs BASELINE:")
            print(f"Distance Reduction: {improvements['distance_reduction_km']:.2f} km "
                  f"({improvements['distance_reduction_percent']:.1f}%)")
            print(f"Cost Savings: ${improvements['cost_savings']:.2f} "
                  f"({improvements['cost_savings_percent']:.1f}%)")

        # Print route details
        print(f"\n🚚 ROUTE DETAILS:")
        for i, route in enumerate(optimized['routes']):
            print(f"  Route {i+1}: {len(route['stops'])-2} deliveries, "
                  f"{route['total_distance']:.1f} km, "
                  f"{route['total_demand']} cylinders")

    def get_solution_for_visualization(self) -> Dict:
        """Get solution data formatted for visualization"""
        if not self.optimized_solution:
            return {}

        viz_data = {
            'delivery_points': self.delivery_data.to_dict('records') if self.delivery_data is not None else [],
            'optimized_routes': self.optimized_solution.get('routes', []),
            'baseline_routes': self.baseline_solution.get('routes', []) if self.baseline_solution else [],
            'improvement_metrics': self.optimized_solution.get('improvement_metrics', {}),
            'depot_location': self._get_scenario_statistics().get('depot_location', {})
        }

        return viz_data


def main():
    """Test function for complete route optimization"""
    # Create optimizer
    optimizer = RouteOptimizer(seed=42)

    # Run complete optimization
    results = optimizer.optimize_single_scenario(
        num_deliveries=25,
        num_vehicles=4,
        time_limit_seconds=30
    )

    print("\n✅ Optimization completed successfully!")
    return results


if __name__ == "__main__":
    main()