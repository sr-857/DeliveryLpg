"""
Mock data generator for LPG delivery points
Creates realistic mixed urban/rural delivery scenarios
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from faker import Faker
import random
from datetime import datetime, timedelta
import math

from ..utils.config import (
    GEOGRAPHIC, DELIVERY, DATA_GENERATION,
    get_generated_data_path
)


class DeliveryPoint:
    """Represents a single delivery point"""

    def __init__(self,
                 id: int,
                 latitude: float,
                 longitude: float,
                 demand: int,
                 time_window_start: datetime,
                 time_window_end: datetime,
                 service_time_minutes: int,
                 priority: str,
                 address: str,
                 area_type: str):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.demand = demand
        self.time_window_start = time_window_start
        self.time_window_end = time_window_end
        self.service_time_minutes = service_time_minutes
        self.priority = priority
        self.address = address
        self.area_type = area_type

    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'demand': self.demand,
            'time_window_start': self.time_window_start.strftime('%H:%M'),
            'time_window_end': self.time_window_end.strftime('%H:%M'),
            'service_time_minutes': self.service_time_minutes,
            'priority': self.priority,
            'address': self.address,
            'area_type': self.area_type
        }


class MockDataGenerator:
    """Generates realistic mock delivery data for mixed urban/rural areas"""

    def __init__(self, seed: Optional[int] = None):
        self.faker = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
            np.random.seed(seed)

    def _generate_urban_points(self, num_points: int) -> List[Tuple[float, float]]:
        """Generate tightly clustered urban delivery points"""
        center_lat, center_lon = GEOGRAPHIC.urban_center
        radius_km = GEOGRAPHIC.urban_radius_km

        points = []
        for _ in range(num_points):
            # Generate points using normal distribution around center
            angle = random.uniform(0, 2 * math.pi)
            # Use normal distribution for more realistic clustering
            distance = np.random.normal(0, radius_km/3)
            distance = min(abs(distance), radius_km)  # Limit to radius

            # Convert distance to lat/lon offset
            lat_offset = distance * math.cos(angle) / 111.32  # ~111.32 km per degree latitude
            lon_offset = distance * math.sin(angle) / (111.32 * math.cos(math.radians(center_lat)))

            lat = center_lat + lat_offset
            lon = center_lon + lon_offset

            points.append((lat, lon))

        return points

    def _generate_rural_points(self, num_points: int) -> List[Tuple[float, float]]:
        """Generate widely spread rural delivery points"""
        points = []

        for _ in range(num_points):
            # Uniform distribution across the wider rural area
            lat = random.uniform(GEOGRAPHIC.lat_min, GEOGRAPHIC.lat_max)
            lon = random.uniform(GEOGRAPHIC.lon_min, GEOGRAPHIC.lon_max)

            # Avoid urban center area
            center_lat, center_lon = GEOGRAPHIC.urban_center
            distance_from_center = self._calculate_distance(center_lat, center_lon, lat, lon)

            # If too close to urban center, regenerate
            if distance_from_center < GEOGRAPHIC.urban_radius_km * 1.5:
                lat = random.uniform(GEOGRAPHIC.lat_min, GEOGRAPHIC.lat_max)
                lon = random.uniform(GEOGRAPHIC.lon_min, GEOGRAPHIC.lon_max)

            points.append((lat, lon))

        return points

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from haversine import haversine
        return haversine((lat1, lon1), (lat2, lon2))

    def _generate_demand(self) -> int:
        """Generate realistic LPG cylinder demand"""
        # Most deliveries are small, some are larger
        weights = [0.6, 0.25, 0.1, 0.05]  # 60% small, 5% large
        demand_ranges = [(1, 5), (6, 10), (11, 15), (16, 20)]

        chosen_range = random.choices(demand_ranges, weights=weights)[0]
        return random.randint(chosen_range[0], chosen_range[1])

    def _generate_time_window(self, base_date: datetime) -> Tuple[datetime, datetime]:
        """Generate delivery time window"""
        start_hour = random.randint(
            DATA_GENERATION.time_window_start_hour,
            DATA_GENERATION.time_window_end_hour - DATA_GENERATION.time_window_duration_hours
        )

        start_time = base_date.replace(hour=start_hour, minute=random.choice([0, 30]))
        end_time = start_time + timedelta(hours=DATA_GENERATION.time_window_duration_hours)

        return start_time, end_time

    def _calculate_service_time(self, demand: int) -> int:
        """Calculate service time based on demand"""
        base_time = DELIVERY.base_service_time_minutes
        additional_time = demand * DELIVERY.service_time_per_cylinder_minutes
        return int(base_time + additional_time)

    def _determine_priority(self) -> str:
        """Determine delivery priority"""
        priorities = list(DELIVERY.priority_distribution.keys())
        weights = list(DELIVERY.priority_distribution.values())
        return random.choices(priorities, weights=weights)[0]

    def _generate_address(self, latitude: float, longitude: float, area_type: str) -> str:
        """Generate realistic address based on area type"""
        if area_type == 'urban':
            # Urban addresses are more specific
            street_types = ['St', 'Ave', 'Dr', 'Rd', 'Blvd', 'Ln']
            street_name = self.faker.street_name()
            street_type = random.choice(street_types)
            number = random.randint(100, 9999)
            return f"{number} {street_name} {street_type}"
        else:
            # Rural addresses use county roads and routes
            county_names = ['Dallas', 'Tarrant', 'Collin', 'Denton', 'Johnson']
            road_types = ['County Road', 'Farm to Market Road', 'Rural Route']
            road_type = random.choice(road_types)
            number = random.randint(1, 999)
            county = random.choice(county_names)
            return f"{number} {road_type} {number}, {county} County"

    def generate_delivery_data(self, num_deliveries: int = None) -> pd.DataFrame:
        """Generate complete delivery dataset"""
        if num_deliveries is None:
            num_deliveries = DATA_GENERATION.default_deliveries

        # Calculate urban/rural split
        num_urban = int(num_deliveries * DATA_GENERATION.urban_percentage)
        num_rural = num_deliveries - num_urban

        # Generate coordinate points
        urban_points = self._generate_urban_points(num_urban)
        rural_points = self._generate_rural_points(num_rural)

        # Combine points and create delivery points
        all_points = urban_points + rural_points
        area_types = ['urban'] * num_urban + ['rural'] * num_rural

        delivery_points = []
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i, ((lat, lon), area_type) in enumerate(zip(all_points, area_types)):
            # Generate delivery characteristics
            demand = self._generate_demand()
            time_start, time_end = self._generate_time_window(base_date)
            service_time = self._calculate_service_time(demand)
            priority = self._determine_priority()
            address = self._generate_address(lat, lon, area_type)

            delivery = DeliveryPoint(
                id=i + 1,  # Start from 1, 0 is reserved for depot
                latitude=lat,
                longitude=lon,
                demand=demand,
                time_window_start=time_start,
                time_window_end=time_end,
                service_time_minutes=service_time,
                priority=priority,
                address=address,
                area_type=area_type
            )

            delivery_points.append(delivery)

        # Convert to DataFrame
        delivery_data = [point.to_dict() for point in delivery_points]
        df = pd.DataFrame(delivery_data)

        # Add depot as first location (center of operations)
        depot_data = {
            'id': 0,
            'latitude': GEOGRAPHIC.center_lat,
            'longitude': GEOGRAPHIC.center_lon,
            'demand': 0,
            'time_window_start': f"{DELIVERY.working_hours_start:02d}:00",
            'time_window_end': f"{DELIVERY.working_hours_end:02d}:00",
            'service_time_minutes': 0,
            'priority': 'depot',
            'address': 'LPG Depot - Central Distribution Center',
            'area_type': 'depot'
        }

        # Add depot at the beginning
        df = pd.concat([pd.DataFrame([depot_data]), df], ignore_index=True)

        return df

    def save_delivery_data(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save delivery data to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"delivery_data_{timestamp}.csv"

        filepath = get_generated_data_path(filename)
        df.to_csv(filepath, index=False)
        return filepath

    def generate_scenario_summary(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics for the scenario"""
        # Exclude depot from calculations
        delivery_df = df[df['id'] != 0]

        total_demand = delivery_df['demand'].sum()
        urban_count = (delivery_df['area_type'] == 'urban').sum()
        rural_count = (delivery_df['area_type'] == 'rural').sum()

        priority_counts = delivery_df['priority'].value_counts().to_dict()

        summary = {
            'total_deliveries': len(delivery_df),
            'total_demand': total_demand,
            'urban_deliveries': urban_count,
            'rural_deliveries': rural_count,
            'priority_distribution': priority_counts,
            'average_demand_per_delivery': total_demand / len(delivery_df) if len(delivery_df) > 0 else 0,
            'depot_location': {
                'latitude': df[df['id'] == 0]['latitude'].iloc[0],
                'longitude': df[df['id'] == 0]['longitude'].iloc[0]
            }
        }

        return summary


def main():
    """Test function for data generation"""
    generator = MockDataGenerator(seed=42)

    # Generate delivery data
    df = generator.generate_delivery_data(num_deliveries=30)

    # Save data
    filepath = generator.save_delivery_data(df)
    print(f"Generated delivery data saved to: {filepath}")

    # Print summary
    summary = generator.generate_scenario_summary(df)
    print("\nScenario Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Print sample data
    print("\nSample delivery points:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()