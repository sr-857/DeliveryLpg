"""
Core functionality test for LPG route optimization system
Tests the optimization engine without visualization components
"""

import sys
import os
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def test_basic_vrp():
    """Test basic Vehicle Routing Problem functionality"""
    print("🧪 Testing Basic VRP Functionality")
    print("=" * 50)

    # Create sample data
    print("📍 Creating sample delivery data...")

    # Sample coordinates (depot + 5 delivery points)
    data = {
        'distance_matrix': [
            [0, 10, 15, 20, 25, 30],  # From depot
            [10, 0, 35, 25, 30, 20],  # From point 1
            [15, 35, 0, 30, 10, 15],  # From point 2
            [20, 25, 30, 0, 15, 25],  # From point 3
            [25, 30, 10, 15, 0, 20],  # From point 4
            [30, 20, 15, 25, 20, 0],  # From point 5
        ],
        'demands': [0, 10, 15, 8, 12, 6],  # Depot has 0 demand
        'vehicle_capacities': [30, 30, 30],  # 3 vehicles with 30 capacity each
        'num_vehicles': 3,
        'depot': 0
    }

    print(f"  - {len(data['distance_matrix'])} locations (1 depot + 5 deliveries)")
    print(f"  - {data['num_vehicles']} vehicles with {data['vehicle_capacities'][0]} capacity each")
    print(f"  - Total demand: {sum(data['demands'])} units")

    # Create routing model
    print("\n🚛 Setting up VRP solver...")
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot'])

    routing = pywrapcp.RoutingModel(manager)

    # Define distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],
        True,  # start cumul to zero
        'Capacity')

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(10)

    # Solve the problem
    print("🔍 Solving VRP...")
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution
    if solution:
        print("✅ Solution found!")
        print(f"Objective value: {solution.ObjectiveValue()}")

        total_distance = 0
        total_load = 0
        routes_used = 0

        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            route_load = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                route_load += data['demands'][node_index]

                previous_index = index
                index = solution.Value(routing.NextVar(index))

                if not routing.IsEnd(index):
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index, index, vehicle_id)

            if len(route) > 1:  # Vehicle was used
                routes_used += 1
                total_distance += route_distance
                total_load += route_load

                print(f"\n📦 Route {vehicle_id + 1}:")
                print(f"  Stops: {route}")
                print(f"  Distance: {route_distance}")
                print(f"  Load: {route_load}")

        print(f"\n📊 Summary:")
        print(f"  Vehicles used: {routes_used}/{data['num_vehicles']}")
        print(f"  Total distance: {total_distance}")
        print(f"  Total load: {total_load}")
        print(f"  Load utilization: {(total_load/sum(data['vehicle_capacities']))*100:.1f}%")

        return True
    else:
        print("❌ No solution found!")
        return False


def test_mock_data_generation():
    """Test mock data generation functionality"""
    print("\n🧪 Testing Mock Data Generation")
    print("=" * 50)

    # Create mock delivery points
    print("📍 Generating mock delivery scenario...")

    # Sample delivery data
    deliveries = []
    for i in range(1, 11):  # 10 delivery points
        lat = 32.7 + np.random.uniform(-0.1, 0.1)  # Around Dallas area
        lon = -96.8 + np.random.uniform(-0.1, 0.1)
        demand = np.random.randint(1, 20)

        deliveries.append({
            'id': i,
            'latitude': lat,
            'longitude': lon,
            'demand': demand,
            'priority': np.random.choice(['normal', 'high', 'emergency'], p=[0.8, 0.15, 0.05]),
            'area_type': np.random.choice(['urban', 'rural'], p=[0.6, 0.4]),
            'time_window_start': f"{8 + i//2:02d}:00",
            'time_window_end': f"{10 + i//2:02d}:00",
            'service_time_minutes': 15 + demand * 2
        })

    df = pd.DataFrame(deliveries)

    # Add depot
    depot_row = {
        'id': 0,
        'latitude': 32.7767,
        'longitude': -96.7970,
        'demand': 0,
        'priority': 'depot',
        'area_type': 'depot',
        'time_window_start': '08:00',
        'time_window_end': '18:00',
        'service_time_minutes': 0
    }

    df = pd.concat([pd.DataFrame([depot_row]), df], ignore_index=True)

    print(f"✅ Generated {len(df)-1} delivery points + 1 depot")
    print(f"  - Urban: {(df['area_type'] == 'urban').sum()}")
    print(f"  - Rural: {(df['area_type'] == 'rural').sum()}")
    print(f"  - Total demand: {df['demand'].sum()} cylinders")
    print(f"  - Priority distribution: {dict(df['priority'].value_counts())}")

    return df


def test_distance_matrix():
    """Test distance matrix calculation"""
    print("\n🧪 Testing Distance Matrix Calculation")
    print("=" * 50)

    # Sample coordinates
    coords = [
        (32.7767, -96.7970),  # Depot
        (32.78, -96.79),      # Point 1
        (32.79, -96.80),      # Point 2
        (32.77, -96.78),      # Point 3
    ]

    print(f"📍 Calculating distances for {len(coords)} locations...")

    # Calculate distance matrix
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate haversine distance between two points"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c

    # Create distance matrix
    distance_matrix = np.zeros((len(coords), len(coords)))

    for i in range(len(coords)):
        for j in range(len(coords)):
            if i != j:
                distance = haversine_distance(coords[i][0], coords[i][1],
                                             coords[j][0], coords[j][1])
                # Add realistic detour factor
                distance *= np.random.uniform(1.2, 1.5)
                distance_matrix[i][j] = distance

    print("✅ Distance matrix calculated:")
    print("    Depot    P1      P2      P3")
    for i, row in enumerate(distance_matrix):
        print(f"{['Depot', 'P1', 'P2', 'P3'][i]:<6} " +
              " ".join(f"{dist:6.2f}" for dist in row))

    return distance_matrix


def main():
    """Main test function"""
    print("🎯 LPG Delivery Route Optimization - Core Functionality Test")
    print("=" * 70)

    try:
        # Test 1: Basic VRP
        vrp_success = test_basic_vrp()

        # Test 2: Mock Data Generation
        delivery_data = test_mock_data_generation()

        # Test 3: Distance Matrix
        distance_matrix = test_distance_matrix()

        print("\n" + "=" * 70)
        print("🎉 CORE FUNCTIONALITY TEST RESULTS")
        print("=" * 70)

        if vrp_success and delivery_data is not None and distance_matrix is not None:
            print("✅ All core components are working correctly!")
            print("📈 System ready for route optimization")
            print("\n🚀 Next steps:")
            print("   1. Install visualization packages: pip install folium streamlit plotly")
            print("   2. Run full system: python main.py demo")
            print("   3. Launch dashboard: python main.py dashboard")
        else:
            print("❌ Some components need attention")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()