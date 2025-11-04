"""
Configuration settings for LPG Delivery Route Optimization System
"""

from dataclasses import dataclass
from typing import Tuple
import os


@dataclass
class GeographicConfig:
    """Geographic configuration for delivery area"""
    # Center point for mixed urban/rural area (example: near Dallas, Texas)
    center_lat: float = 32.7767
    center_lon: float = -96.7970

    # Area bounds (50km x 50km area)
    lat_min: float = 32.5
    lat_max: float = 33.0
    lon_min: float = -97.1
    lon_max: float = -96.5

    # Urban cluster configuration
    urban_center: Tuple[float, float] = (32.7767, -96.7970)
    urban_radius_km: float = 10.0

    # Rural spread configuration
    rural_delivery_ratio: float = 0.4  # 40% rural deliveries


@dataclass
class DeliveryConfig:
    """Delivery operation configuration"""
    # Vehicle specifications
    vehicle_capacity: int = 80  # LPG cylinders per truck
    max_route_duration_hours: float = 8.0
    working_hours_start: int = 8  # 8:00 AM
    working_hours_end: int = 18   # 6:00 PM

    # Speed constraints (km/h)
    urban_speed_kmh: float = 30.0
    rural_speed_kmh: float = 60.0

    # Service times (minutes)
    base_service_time_minutes: int = 15
    service_time_per_cylinder_minutes: float = 0.75

    # Fuel cost calculation
    fuel_cost_per_gallon: float = 3.50
    fuel_efficiency_mpg: float = 8.0

    # Delivery priorities
    priority_distribution = {
        'normal': 0.8,
        'high': 0.15,
        'emergency': 0.05
    }


@dataclass
class DataGenerationConfig:
    """Mock data generation configuration"""
    # Number of delivery points
    min_deliveries: int = 25
    max_deliveries: int = 40
    default_deliveries: int = 30

    # Demand configuration (LPG cylinders)
    min_demand: int = 1
    max_demand: int = 20

    # Time window configuration
    time_window_duration_hours: int = 2
    time_window_start_hour: int = 8
    time_window_end_hour: int = 16

    # Urban/rural split
    urban_percentage: float = 0.6  # 60% urban, 40% rural


@dataclass
class OptimizationConfig:
    """OR-Tools optimization configuration"""
    # Solver parameters
    solver_time_limit_seconds: int = 30
    first_solution_strategy: str = "PATH_CHEAPEST_ARC"
    local_search_metaheuristic: str = "GUIDED_LOCAL_SEARCH"

    # Solution parameters
    max_vehicles: int = 10
    allow_multiple_vehicles: bool = True

    # Constraint weights
    distance_weight: float = 1.0
    time_weight: float = 0.5
    capacity_weight: float = 10.0


@dataclass
class VisualizationConfig:
    """Dashboard and visualization configuration"""
    # Map configuration
    map_zoom_start: int = 10
    tile_layer: str = "OpenStreetMap"

    # Route colors
    before_route_color: str = "red"
    after_route_color: str = "green"
    depot_color: str = "blue"

    # Dashboard configuration
    dashboard_title: str = "LPG Delivery Route Optimization"
    page_width: int = 1200

    # Performance targets
    target_distance_reduction_percent: float = 20.0
    target_optimization_time_seconds: float = 30.0
    target_dashboard_load_time_seconds: float = 5.0


# Global configuration instances
GEOGRAPHIC = GeographicConfig()
DELIVERY = DeliveryConfig()
DATA_GENERATION = DataGenerationConfig()
OPTIMIZATION = OptimizationConfig()
VISUALIZATION = VisualizationConfig()


# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
GENERATED_DATA_DIR = os.path.join(DATA_DIR, "generated")
OUTPUT_DATA_DIR = os.path.join(DATA_DIR, "output")


def get_output_path(filename: str) -> str:
    """Get full path for output file"""
    return os.path.join(OUTPUT_DATA_DIR, filename)


def get_generated_data_path(filename: str) -> str:
    """Get full path for generated data file"""
    return os.path.join(GENERATED_DATA_DIR, filename)