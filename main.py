"""
Main entry point for LPG Delivery Route Optimization System
Provides command-line interface for running optimization and launching dashboard
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from optimization.route_optimizer import RouteOptimizer
from visualization.dashboard import Dashboard
from utils.config import DATA_GENERATION, OPTIMIZATION
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data/generated",
        "data/output",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


def run_optimization_cli(args):
    """Run optimization from command line interface"""
    logger.info("Starting LPG Delivery Route Optimization (CLI mode)")

    try:
        # Initialize optimizer
        optimizer = RouteOptimizer(seed=args.seed)

        # Generate delivery scenario
        logger.info(f"Generating scenario with {args.deliveries} deliveries...")
        delivery_data, scenario_summary = optimizer.generate_delivery_scenario(
            num_deliveries=args.deliveries
        )

        logger.info(f"✓ Generated {scenario_summary['total_deliveries']} deliveries")
        logger.info(f"  - Urban: {scenario_summary['urban_deliveries']}, Rural: {scenario_summary['rural_deliveries']}")
        logger.info(f"  - Total demand: {scenario_summary['total_demand']} LPG cylinders")

        # Calculate distance matrices
        logger.info("Calculating distance and time matrices...")
        matrix_stats = optimizer.calculate_distance_matrices()
        logger.info(f"✓ Matrices calculated in {matrix_stats['matrix_calculation_time_seconds']:.2f}s")

        # Run optimization
        logger.info("Running route optimization...")
        results = optimizer.optimize_single_scenario(
            num_deliveries=args.deliveries,
            num_vehicles=args.vehicles,
            time_limit_seconds=args.time_limit
        )

        # Print results summary
        print_optimization_summary(results, args.verbose)

        # Save results if requested
        if args.save:
            save_results(results, args.output_file)

        logger.info("✅ Optimization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Optimization failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_optimization_summary(results, verbose=False):
    """Print optimization results summary"""
    print("\n" + "=" * 60)
    print("LPG DELIVERY ROUTE OPTIMIZATION RESULTS")
    print("=" * 60)

    # Optimization info
    opt_info = results.get('optimization_info', {})
    print(f"Solver Status: {opt_info.get('solver_status', 'Unknown')}")
    print(f"Total Optimization Time: {opt_info.get('total_optimization_time_seconds', 0):.2f} seconds")
    print(f"Deliveries Processed: {opt_info.get('num_deliveries', 0)}")

    # Optimized solution results
    optimized = results.get('optimized_solution', {})
    if optimized.get('status') == 'no_solution':
        print("\n❌ No feasible solution found")
        return

    print(f"\n📊 OPTIMIZED SOLUTION:")
    print(f"Total Distance: {optimized.get('total_distance', 0):.2f} km")
    print(f"Vehicles Used: {optimized.get('num_vehicles_used', 0)}")
    print(f"Total Demand Served: {optimized.get('total_demand_served', 0)} cylinders")

    # Route details
    routes = optimized.get('routes', [])
    print(f"\n🚚 ROUTE DETAILS:")
    for i, route in enumerate(routes):
        deliveries = len(route.get('stops', [])) - 2  # Exclude depot
        print(f"  Route {i+1}: {deliveries} deliveries, "
              f"{route.get('total_distance', 0):.1f} km, "
              f"{route.get('total_demand', 0)} cylinders")

    # Improvement metrics if available
    if 'improvement_metrics' in results:
        improvements = results.get('improvement_metrics', {})
        print(f"\n📈 IMPROVEMENTS vs BASELINE:")
        print(f"Distance Reduction: {improvements.get('distance_reduction_km', 0):.2f} km "
              f"({improvements.get('distance_reduction_percent', 0):.1f}%)")
        print(f"Cost Savings: ${improvements.get('cost_savings', 0):.2f} "
              f"({improvements.get('cost_savings_percent', 0):.1f}%)")
        print(f"Vehicles Reduced: {improvements.get('vehicles_reduction', 0)}")

    # Verbose output
    if verbose and 'scenario_statistics' in results:
        stats = results.get('scenario_statistics', {})
        print(f"\n📋 SCENARIO STATISTICS:")
        print(f"Urban Deliveries: {stats.get('urban_deliveries', 0)}")
        print(f"Rural Deliveries: {stats.get('rural_deliveries', 0)}")
        print(f"Priority Distribution: {stats.get('priority_distribution', {})}")


def save_results(results, output_file=None):
    """Save optimization results to file"""
    import json

    if output_file is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"optimization_results_{timestamp}.json"

    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to: {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {str(e)}")


def launch_dashboard(args):
    """Launch Streamlit dashboard"""
    logger.info("Launching LPG Delivery Route Optimization Dashboard")

    try:
        # Import and run dashboard
        dashboard = Dashboard()

        # Store launch args in session state if needed
        if hasattr(args, 'sample') and args.sample:
            # Auto-load sample data if requested
            dashboard._load_sample_scenario()

        # Run dashboard (this will block until the dashboard is closed)
        dashboard.run()

    except Exception as e:
        logger.error(f"❌ Failed to launch dashboard: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_demo():
    """Run a complete demonstration of the system"""
    logger.info("🎬 Running LPG Delivery Route Optimization Demo")

    try:
        # Initialize optimizer with demo seed
        optimizer = RouteOptimizer(seed=42)

        # Run demo optimization
        print("\n🎬 LPG DELIVERY ROUTE OPTIMIZATION DEMO")
        print("=" * 50)

        # Generate demo scenario
        delivery_data, scenario_summary = optimizer.generate_delivery_scenario(
            num_deliveries=30
        )

        print(f"✓ Generated demo scenario with {scenario_summary['total_deliveries']} deliveries")
        print(f"  - Urban: {scenario_summary['urban_deliveries']}, Rural: {scenario_summary['rural_deliveries']}")
        print(f"  - Total demand: {scenario_summary['total_demand']} LPG cylinders")

        # Calculate distance matrices
        matrix_stats = optimizer.calculate_distance_matrices()
        print(f"✓ Distance matrices calculated")

        # Run optimization
        results = optimizer.optimize_single_scenario(
            num_deliveries=30,
            num_vehicles=4,
            time_limit_seconds=30
        )

        # Print demo results
        print_optimization_summary(results, verbose=True)

        print(f"\n🎉 Demo completed successfully!")
        print(f"💡 To explore the interactive dashboard, run: python main.py dashboard")

        return results

    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="LPG Delivery Route Optimization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py demo                           # Run demonstration
  python main.py optimize --deliveries 25       # Optimize 25 deliveries
  python main.py optimize --vehicles 5 --save   # Use 5 vehicles and save results
  python main.py dashboard                      # Launch interactive dashboard
  python main.py dashboard --sample             # Launch with sample data
        """
    )

    parser.add_argument(
        'action',
        choices=['demo', 'optimize', 'dashboard'],
        help='Action to perform'
    )

    # Optimization arguments
    parser.add_argument('--deliveries', type=int, default=30,
                       help='Number of deliveries to generate (default: 30)')
    parser.add_argument('--vehicles', type=int, default=4,
                       help='Number of vehicles to use (default: 4)')
    parser.add_argument('--time-limit', type=int, default=30,
                       help='Solver time limit in seconds (default: 30)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducible results')

    # Output arguments
    parser.add_argument('--save', action='store_true',
                       help='Save results to file')
    parser.add_argument('--output-file', type=str, default=None,
                       help='Output file name (default: auto-generated)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    # Dashboard arguments
    parser.add_argument('--sample', action='store_true',
                       help='Load sample data in dashboard')

    args = parser.parse_args()

    # Setup directories
    setup_directories()

    # Execute requested action
    if args.action == 'demo':
        results = run_demo()
        sys.exit(0 if results else 1)

    elif args.action == 'optimize':
        run_optimization_cli(args)
        sys.exit(0)

    elif args.action == 'dashboard':
        # Note: Streamlit has its own CLI, so we need to handle this differently
        import subprocess
        import os

        # Get the path to the dashboard script
        dashboard_script = Path(__file__).parent / "src" / "visualization" / "dashboard.py"

        # Build streamlit command
        cmd = [
            'streamlit', 'run', str(dashboard_script),
            '--server.headless', 'false',
            '--server.port', '8501'
        ]

        if args.sample:
            # Pass sample flag via environment variable
            os.environ['LOAD_SAMPLE_DATA'] = 'true'

        print("🚀 Launching Streamlit dashboard...")
        print(f"   Dashboard will be available at: http://localhost:8501")
        print(f"   Press Ctrl+C to stop the dashboard")
        print()

        # Run streamlit
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped by user")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to launch dashboard: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ Streamlit not found. Please install it with: pip install streamlit")
            sys.exit(1)


if __name__ == "__main__":
    main()