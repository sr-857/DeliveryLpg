"""
Distance matrix calculation for route optimization
Computes realistic road distances and travel times between delivery points
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
import time
import math

from ..utils.config import DELIVERY, GEOGRAPHIC


class DistanceMatrix:
    """Computes and manages distance/time matrices for route optimization"""

    def __init__(self, delivery_data: pd.DataFrame):
        self.delivery_data = delivery_data
        self.num_locations = len(delivery_data)
        self.distance_matrix = None
        self.time_matrix = None
        self.coordinates = self._extract_coordinates()

    def _extract_coordinates(self) -> List[Tuple[float, float]]:
        """Extract coordinates from delivery data"""
        coords = []
        for _, row in self.delivery_data.iterrows():
            coords.append((row['latitude'], row['longitude']))
        return coords

    def _determine_area_type(self, lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """Determine if route is primarily urban or rural"""
        # Check if both points are near urban center
        center_lat, center_lon = GEOGRAPHIC.urban_center
        urban_radius_km = GEOGRAPHIC.urban_radius_km

        # Calculate distance from urban center for both points
        from haversine import haversine
        dist1 = haversine((center_lat, center_lon), (lat1, lon1))
        dist2 = haversine((center_lat, center_lon), (lat2, lon2))

        # If both points are in urban area, consider urban route
        if dist1 <= urban_radius_km and dist2 <= urban_radius_km:
            return 'urban'
        # If both are far from urban center, consider rural route
        elif dist1 > urban_radius_km * 1.5 and dist2 > urban_radius_km * 1.5:
            return 'rural'
        else:
            # Mixed route - use weighted average
            return 'mixed'

    def _calculate_realistic_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate realistic road distance accounting for urban/rural routing
        """
        # Get straight-line distance as base
        from haversine import haversine
        straight_distance = haversine((lat1, lon1), (lat2, lon2))

        # Determine route type
        route_type = self._determine_area_type(lat1, lon1, lat2, lon2)

        # Apply realistic detour factors based on route type
        if route_type == 'urban':
            # Urban routes have more detours due to one-way streets, traffic
            detour_factor = np.random.uniform(1.3, 1.6)
        elif route_type == 'rural':
            # Rural routes are closer to straight-line but have some detours
            detour_factor = np.random.uniform(1.1, 1.3)
        else:  # mixed
            # Mixed routes combine urban and rural characteristics
            detour_factor = np.random.uniform(1.2, 1.4)

        realistic_distance = straight_distance * detour_factor
        return realistic_distance

    def _calculate_travel_time(self, distance_km: float, lat1: float, lon1: float,
                              lat2: float, lon2: float) -> float:
        """Calculate travel time based on distance and route characteristics"""
        # Determine route type to get appropriate speed
        route_type = self._determine_area_type(lat1, lon1, lat2, lon2)

        if route_type == 'urban':
            # Urban routes are slower due to traffic, stops
            base_speed = DELIVERY.urban_speed_kmh
            # Add some randomness for realistic variation
            speed_factor = np.random.uniform(0.7, 1.0)
        elif route_type == 'rural':
            # Rural routes are faster
            base_speed = DELIVERY.rural_speed_kmh
            speed_factor = np.random.uniform(0.9, 1.0)
        else:  # mixed
            # Mixed routes use weighted average
            urban_weight = 0.6  # Slightly more urban influence
            rural_weight = 0.4
            base_speed = (DELIVERY.urban_speed_kmh * urban_weight +
                         DELIVERY.rural_speed_kmh * rural_weight)
            speed_factor = np.random.uniform(0.8, 1.0)

        actual_speed = base_speed * speed_factor
        travel_time_hours = distance_km / actual_speed
        travel_time_minutes = travel_time_hours * 60

        return travel_time_minutes

    def compute_distance_matrix(self, use_cache: bool = True) -> np.ndarray:
        """
        Compute distance matrix for all location pairs
        Returns matrix where matrix[i][j] is distance from i to j in kilometers
        """
        if self.distance_matrix is not None and use_cache:
            return self.distance_matrix

        print(f"Computing distance matrix for {self.num_locations} locations...")
        start_time = time.time()

        # Initialize distance matrix
        distance_matrix = np.zeros((self.num_locations, self.num_locations))

        # Calculate distances between all pairs
        for i in range(self.num_locations):
            lat1, lon1 = self.coordinates[i]
            for j in range(self.num_locations):
                if i != j:
                    lat2, lon2 = self.coordinates[j]
                    distance = self._calculate_realistic_distance(lat1, lon1, lat2, lon2)
                    distance_matrix[i][j] = distance

        self.distance_matrix = distance_matrix

        elapsed_time = time.time() - start_time
        print(f"Distance matrix computed in {elapsed_time:.2f} seconds")

        return distance_matrix

    def compute_time_matrix(self, use_cache: bool = True) -> np.ndarray:
        """
        Compute time matrix for all location pairs
        Returns matrix where matrix[i][j] is travel time from i to j in minutes
        """
        if self.time_matrix is not None and use_cache:
            return self.time_matrix

        print(f"Computing time matrix for {self.num_locations} locations...")
        start_time = time.time()

        # Ensure distance matrix is computed
        if self.distance_matrix is None:
            self.compute_distance_matrix()

        # Initialize time matrix
        time_matrix = np.zeros((self.num_locations, self.num_locations))

        # Calculate travel times
        for i in range(self.num_locations):
            lat1, lon1 = self.coordinates[i]
            for j in range(self.num_locations):
                if i != j:
                    lat2, lon2 = self.coordinates[j]
                    distance_km = self.distance_matrix[i][j]
                    travel_time = self._calculate_travel_time(
                        distance_km, lat1, lon1, lat2, lon2
                    )
                    time_matrix[i][j] = travel_time

        self.time_matrix = time_matrix

        elapsed_time = time.time() - start_time
        print(f"Time matrix computed in {elapsed_time:.2f} seconds")

        return time_matrix

    def get_distance(self, from_location: int, to_location: int) -> float:
        """Get distance between two specific locations"""
        if self.distance_matrix is None:
            self.compute_distance_matrix()
        return self.distance_matrix[from_location][to_location]

    def get_travel_time(self, from_location: int, to_location: int) -> float:
        """Get travel time between two specific locations in minutes"""
        if self.time_matrix is None:
            self.compute_time_matrix()
        return self.time_matrix[from_location][to_location]

    def get_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get both distance and time matrices"""
        distance_matrix = self.compute_distance_matrix()
        time_matrix = self.compute_time_matrix()
        return distance_matrix, time_matrix

    def get_matrix_statistics(self) -> Dict:
        """Get statistics about the computed matrices"""
        if self.distance_matrix is None or self.time_matrix is None:
            self.get_matrices()

        # Remove zero values (diagonal) from statistics
        distance_values = self.distance_matrix[self.distance_matrix > 0]
        time_values = self.time_matrix[self.time_matrix > 0]

        stats = {
            'num_locations': self.num_locations,
            'distance_stats': {
                'min_km': float(np.min(distance_values)),
                'max_km': float(np.max(distance_values)),
                'mean_km': float(np.mean(distance_values)),
                'std_km': float(np.std(distance_values))
            },
            'time_stats': {
                'min_minutes': float(np.min(time_values)),
                'max_minutes': float(np.max(time_values)),
                'mean_minutes': float(np.mean(time_values)),
                'std_minutes': float(np.std(time_values))
            },
            'total_distance_km': float(np.sum(distance_values)),
            'total_time_minutes': float(np.sum(time_values))
        }

        return stats

    def save_matrices(self, output_path: str = None) -> Dict[str, str]:
        """Save distance and time matrices to files"""
        import os
        from ..utils.config import get_output_path

        if output_path is None:
            timestamp = int(time.time())
            base_path = get_output_path(f"matrices_{timestamp}")
        else:
            base_path = output_path

        # Save distance matrix
        distance_path = f"{base_path}_distance.csv"
        np.savetxt(distance_path, self.distance_matrix, delimiter=',')

        # Save time matrix
        time_path = f"{base_path}_time.csv"
        np.savetxt(time_path, self.time_matrix, delimiter=',')

        # Save statistics
        stats_path = f"{base_path}_stats.json"
        import json
        stats = self.get_matrix_statistics()
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        return {
            'distance_matrix': distance_path,
            'time_matrix': time_path,
            'statistics': stats_path
        }


def main():
    """Test function for distance matrix calculation"""
    from .mock_data_generator import MockDataGenerator

    # Generate test data
    generator = MockDataGenerator(seed=42)
    delivery_data = generator.generate_delivery_data(num_deliveries=10)

    # Create distance matrix
    distance_matrix = DistanceMatrix(delivery_data)

    # Compute matrices
    dist_matrix, time_matrix = distance_matrix.get_matrices()

    # Print statistics
    stats = distance_matrix.get_matrix_statistics()
    print("Distance Matrix Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test specific queries
    depot = 0  # First location is depot
    first_delivery = 1
    distance = distance_matrix.get_distance(depot, first_delivery)
    travel_time = distance_matrix.get_travel_time(depot, first_delivery)

    print(f"\nExample: Depot to Delivery {first_delivery}")
    print(f"  Distance: {distance:.2f} km")
    print(f"  Travel time: {travel_time:.1f} minutes")


if __name__ == "__main__":
    main()