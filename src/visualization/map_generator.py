"""
Folium map generator for LPG delivery route visualization
Creates interactive before/after route comparison maps
"""

import folium
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
import branca.colormap as cm
from folium import plugins

from ..utils.config import VISUALIZATION, GEOGRAPHIC


class MapGenerator:
    """Generates interactive maps for route visualization"""

    def __init__(self):
        self.map_colors = {
            'before_route': VISUALIZATION.before_route_color,
            'after_route': VISUALIZATION.after_route_color,
            'depot': VISUALIZATION.depot_color,
            'urban_delivery': 'orange',
            'rural_delivery': 'purple',
            'high_priority': 'red',
            'normal_priority': 'blue',
            'emergency_priority': 'darkred'
        }

    def create_base_map(self, center_lat: float = None, center_lon: float = None,
                       zoom_start: int = None) -> folium.Map:
        """Create base map with appropriate center and zoom"""
        if center_lat is None:
            center_lat = GEOGRAPHIC.center_lat
        if center_lon is None:
            center_lon = GEOGRAPHIC.center_lon
        if zoom_start is None:
            zoom_start = VISUALIZATION.map_zoom_start

        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles=VISUALIZATION.tile_layer
        )

        # Add alternative tile layers
        folium.TileLayer('CartoDB positron', name='Light Theme').add_to(m)
        folium.TileLayer('OpenStreetMap', name='Standard').add_to(m)

        return m

    def add_delivery_points(self, map_obj: folium.Map, delivery_data: pd.DataFrame,
                          show_labels: bool = True) -> None:
        """Add delivery points as markers to the map"""
        for _, row in delivery_data.iterrows():
            location_id = row['id']
            lat = row['latitude']
            lon = row['longitude']
            demand = row['demand']
            priority = row['priority']
            area_type = row['area_type']
            address = row['address']

            # Determine marker color and icon
            if location_id == 0:  # Depot
                color = self.map_colors['depot']
                icon = 'warehouse'
                prefix = 'fa'
            else:
                # Color based on priority
                if priority == 'emergency':
                    color = self.map_colors['emergency_priority']
                elif priority == 'high':
                    color = self.map_colors['high_priority']
                else:
                    color = self.map_colors['normal_priority']

                # Icon based on area type
                icon = 'home' if area_type == 'urban' else 'building'
                prefix = 'fa'

            # Create popup content
            popup_content = self._create_delivery_popup(row)

            # Create tooltip
            tooltip = f"ID: {location_id}, Demand: {demand} cylinders" if location_id != 0 else "LPG Depot"

            # Add marker
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=tooltip,
                icon=folium.Icon(color=color, icon=icon, prefix=prefix)
            ).add_to(map_obj)

            # Add text label if requested
            if show_labels and location_id != 0:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=15,
                    color='white',
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_content, max_width=300)
                ).add_to(map_obj)

                # Add label text
                folium.map.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 8pt; font-weight: bold; color: white; text-align: center;">{location_id}</div>',
                        icon_size=(20, 20),
                        icon_anchor=(10, 10)
                    )
                ).add_to(map_obj)

    def _create_delivery_popup(self, row) -> str:
        """Create HTML popup content for delivery point"""
        if row['id'] == 0:  # Depot
            return f"""
            <div style="width: 200px;">
                <h4 style="color: {self.map_colors['depot']};">🏭 LPG Depot</h4>
                <p><strong>Address:</strong> {row['address']}</p>
                <p><strong>Location:</strong> {row['latitude']:.4f}, {row['longitude']:.4f}</p>
            </div>
            """
        else:
            priority_emoji = {'emergency': '🚨', 'high': '⚡', 'normal': '📦'}.get(row['priority'], '📦')
            area_type_emoji = {'urban': '🏙️', 'rural': '🌾', 'depot': '🏭'}.get(row['area_type'], '📍')

            return f"""
            <div style="width: 250px;">
                <h4 style="color: {self.map_colors.get(row['priority'], 'blue')};">
                    {priority_emoji} Delivery Point #{row['id']}
                </h4>
                <p><strong>{area_type_emoji} Area Type:</strong> {row['area_type'].title()}</p>
                <p><strong>📦 Demand:</strong> {row['demand']} LPG cylinders</p>
                <p><strong>⏰ Time Window:</strong> {row['time_window_start']} - {row['time_window_end']}</p>
                <p><strong>⏱️ Service Time:</strong> {row['service_time_minutes']} minutes</p>
                <p><strong>🚨 Priority:</strong> {row['priority'].title()}</p>
                <p><strong>📍 Address:</strong> {row['address']}</p>
                <p><strong>🌍 Location:</strong> {row['latitude']:.4f}, {row['longitude']:.4f}</p>
            </div>
            """

    def add_route_lines(self, map_obj: folium.Map, routes: List[Dict],
                       delivery_data: pd.DataFrame, route_color: str = 'blue',
                       line_weight: int = 3, line_opacity: float = 0.8,
                       show_arrows: bool = True, show_route_numbers: bool = True) -> None:
        """Add route lines to the map"""
        # Create coordinate lookup
        coord_lookup = {row['id']: (row['latitude'], row['longitude'])
                       for _, row in delivery_data.iterrows()}

        for route_idx, route in enumerate(routes):
            if len(route.get('stops', [])) < 2:
                continue

            # Get route coordinates
            route_coords = []
            for stop_id in route['stops']:
                if stop_id in coord_lookup:
                    route_coords.append(coord_lookup[stop_id])

            if len(route_coords) < 2:
                continue

            # Create route line
            folium.PolyLine(
                locations=route_coords,
                color=route_color,
                weight=line_weight,
                opacity=line_opacity,
                popup=f"Route {route_idx + 1}<br>"
                      f"Distance: {route.get('total_distance', 0):.1f} km<br>"
                      f"Deliveries: {len(route.get('stops', [])) - 2}<br>"
                      f"Demand: {route.get('total_demand', 0)} cylinders"
            ).add_to(map_obj)

            # Add directional arrows
            if show_arrows and len(route_coords) > 1:
                self._add_directional_arrows(map_obj, route_coords, route_color)

            # Add route number label
            if show_route_numbers and len(route_coords) > 1:
                mid_idx = len(route_coords) // 2
                mid_point = route_coords[mid_idx]

                folium.Marker(
                    location=mid_point,
                    icon=folium.DivIcon(
                        html=f'<div style="background-color: {route_color}; color: white; '
                             f'border-radius: 50%; width: 25px; height: 25px; '
                             f'display: flex; align-items: center; justify-content: center; '
                             f'font-weight: bold; font-size: 12px;">{route_idx + 1}</div>',
                        icon_size=(25, 25),
                        icon_anchor=(12, 12)
                    )
                ).add_to(map_obj)

    def _add_directional_arrows(self, map_obj: folium.Map, route_coords: List[Tuple[float, float]],
                               color: str, arrow_interval: int = 3) -> None:
        """Add directional arrows along route"""
        for i in range(0, len(route_coords) - 1, arrow_interval):
            if i + 1 < len(route_coords):
                start = route_coords[i]
                end = route_coords[i + 1]

                # Calculate arrow position (midpoint)
                mid_lat = (start[0] + end[0]) / 2
                mid_lon = (start[1] + end[1]) / 2

                # Calculate arrow direction
                angle = np.degrees(np.arctan2(end[1] - start[1], end[0] - start[0]))

                # Add arrow marker
                folium.RegularPolygonMarker(
                    location=[mid_lat, mid_lon],
                    popup='Route Direction',
                    number_of_sides=3,
                    radius=8,
                    rotation=angle,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8
                ).add_to(map_obj)

    def create_before_after_map(self, delivery_data: pd.DataFrame,
                              baseline_routes: List[Dict],
                              optimized_routes: List[Dict],
                              save_html: bool = False) -> folium.Map:
        """
        Create a before/after comparison map with both route sets

        Args:
            delivery_data: DataFrame with delivery point information
            baseline_routes: List of baseline routes
            optimized_routes: List of optimized routes
            save_html: Whether to save the map as HTML file

        Returns:
            Folium map object
        """
        # Calculate center point
        center_lat = delivery_data['latitude'].mean()
        center_lon = delivery_data['longitude'].mean()

        # Create base map
        m = self.create_base_map(center_lat, center_lon, zoom_start=10)

        # Add delivery points
        self.add_delivery_points(m, delivery_data, show_labels=True)

        # Add baseline routes (red/orange)
        if baseline_routes:
            self.add_route_lines(
                m, baseline_routes, delivery_data,
                route_color=self.map_colors['before_route'],
                line_weight=3, line_opacity=0.6,
                show_arrows=True, show_route_numbers=True
            )

        # Add optimized routes (green)
        if optimized_routes:
            self.add_route_lines(
                m, optimized_routes, delivery_data,
                route_color=self.map_colors['after_route'],
                line_weight=4, line_opacity=0.8,
                show_arrows=True, show_route_numbers=True
            )

        # Add legend
        self._add_legend(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Add scale bar
        plugins.MeasureControl().add_to(m)

        # Add fullscreen button
        plugins.Fullscreen().add_to(m)

        # Save if requested
        if save_html:
            import os
            from ..utils.config import get_output_path
            timestamp = int(pd.Timestamp.now().timestamp())
            filename = f"route_comparison_map_{timestamp}.html"
            filepath = get_output_path(filename)
            m.save(filepath)
            print(f"Map saved to: {filepath}")

        return m

    def _add_legend(self, map_obj: folium.Map) -> None:
        """Add legend to the map"""
        legend_html = """
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 200px; height: 180px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <h4 style="margin-top: 0; color: #333;">Route Legend</h4>
        <p><i class="fa fa-circle" style="color:{depot_color}"></i> LPG Depot</p>
        <p><i class="fa fa-circle" style="color:{before_color}"></i> Before Optimization</p>
        <p><i class="fa fa-circle" style="color:{after_color}"></i> After Optimization</p>
        <p><i class="fa fa-circle" style="color:orange"></i> Urban Delivery</p>
        <p><i class="fa fa-circle" style="color:purple"></i> Rural Delivery</p>
        <p><i class="fa fa-circle" style="color:red"></i> Emergency Priority</p>
        <p><i class="fa fa-circle" style="color:blue"></i> Normal Priority</p>
        </div>
        """.format(
            depot_color=self.map_colors['depot'],
            before_color=self.map_colors['before_route'],
            after_color=self.map_colors['after_route']
        )

        map_obj.get_root().html.add_child(folium.Element(legend_html))

    def create_route_analysis_map(self, delivery_data: pd.DataFrame,
                                routes: List[Dict], route_type: str = 'optimized',
                                show_analysis: bool = True) -> folium.Map:
        """
        Create detailed route analysis map for a single route set

        Args:
            delivery_data: DataFrame with delivery point information
            routes: List of routes to visualize
            route_type: Type of routes ('optimized' or 'baseline')
            show_analysis: Whether to show detailed analysis information

        Returns:
            Folium map object
        """
        # Calculate center point
        center_lat = delivery_data['latitude'].mean()
        center_lon = delivery_data['longitude'].mean()

        # Create base map
        m = self.create_base_map(center_lat, center_lon, zoom_start=11)

        # Add delivery points
        self.add_delivery_points(m, delivery_data, show_labels=True)

        # Choose color based on route type
        route_color = (self.map_colors['after_route'] if route_type == 'optimized'
                      else self.map_colors['before_route'])

        # Add routes
        self.add_route_lines(
            m, routes, delivery_data,
            route_color=route_color,
            line_weight=4, line_opacity=0.8,
            show_arrows=True, show_route_numbers=True
        )

        # Add detailed analysis if requested
        if show_analysis:
            self._add_route_analysis_panel(m, routes, delivery_data, route_type)

        # Add legend and controls
        self._add_legend(m)
        folium.LayerControl().add_to(m)
        plugins.MeasureControl().add_to(m)
        plugins.Fullscreen().add_to(m)

        return m

    def _add_route_analysis_panel(self, map_obj: folium.Map, routes: List[Dict],
                                delivery_data: pd.DataFrame, route_type: str) -> None:
        """Add route analysis panel to map"""
        # Calculate route statistics
        total_distance = sum(route.get('total_distance', 0) for route in routes)
        total_deliveries = sum(len(route.get('stops', [])) - 2 for route in routes)
        total_demand = sum(route.get('total_demand', 0) for route in routes)

        analysis_html = f"""
        <div style="position: fixed;
                    top: 10px; right: 10px; width: 250px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:12px; padding: 10px; border-radius: 5px">
        <h4 style="margin-top: 0; color: #333;">{route_type.title()} Routes Analysis</h4>
        <p><strong>🚚 Total Routes:</strong> {len(routes)}</p>
        <p><strong>📦 Total Deliveries:</strong> {total_deliveries}</p>
        <p><strong>📊 Total Demand:</strong> {total_demand} cylinders</p>
        <p><strong>🛣️ Total Distance:</strong> {total_distance:.1f} km</p>
        <p><strong>⚡ Avg Distance/Route:</strong> {total_distance/len(routes):.1f} km</p>
        <p><strong>📈 Avg Deliveries/Route:</strong> {total_deliveries/len(routes):.1f}</p>
        </div>
        """

        map_obj.get_root().html.add_child(folium.Element(analysis_html))

    def create_heat_map(self, delivery_data: pd.DataFrame, metric_column: str = 'demand') -> folium.Map:
        """
        Create a heat map showing delivery density or demand

        Args:
            delivery_data: DataFrame with delivery point information
            metric_column: Column to use for heat map intensity

        Returns:
            Folium map with heat map overlay
        """
        # Calculate center point
        center_lat = delivery_data['latitude'].mean()
        center_lon = delivery_data['longitude'].mean()

        # Create base map
        m = self.create_base_map(center_lat, center_lon, zoom_start=10)

        # Prepare heat map data
        heat_data = []
        for _, row in delivery_data.iterrows():
            if row['id'] != 0:  # Exclude depot
                weight = row[metric_column] if metric_column in row else 1
                heat_data.append([row['latitude'], row['longitude'], weight])

        # Add heat map
        plugins.HeatMap(
            heat_data,
            name=f'{metric_column.title()} Heat Map',
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(m)

        # Add delivery points as markers
        self.add_delivery_points(m, delivery_data, show_labels=False)

        # Add layer control
        folium.LayerControl().add_to(m)

        return m


def main():
    """Test function for map generation"""
    # Create test data
    delivery_data = pd.DataFrame({
        'id': [0, 1, 2, 3, 4],
        'latitude': [32.7767, 32.78, 32.79, 32.77, 32.76],
        'longitude': [-96.7970, -96.79, -96.80, -96.78, -96.81],
        'demand': [0, 10, 15, 8, 12],
        'priority': ['depot', 'normal', 'high', 'normal', 'emergency'],
        'area_type': ['depot', 'urban', 'urban', 'rural', 'rural'],
        'address': ['Depot', '123 Main St', '456 Oak Ave', '789 Country Rd', '321 Farm Rd'],
        'time_window_start': ['08:00', '08:00', '09:00', '10:00', '11:00'],
        'time_window_end': ['18:00', '10:00', '11:00', '12:00', '13:00'],
        'service_time_minutes': [0, 20, 25, 18, 22]
    })

    # Create test routes
    baseline_routes = [
        {
            'stops': [0, 1, 3, 4, 0],
            'total_distance': 25.5,
            'total_demand': 30
        },
        {
            'stops': [0, 2, 0],
            'total_distance': 12.3,
            'total_demand': 15
        }
    ]

    optimized_routes = [
        {
            'stops': [0, 1, 2, 0],
            'total_distance': 18.2,
            'total_demand': 25
        },
        {
            'stops': [0, 3, 4, 0],
            'total_distance': 15.8,
            'total_demand': 20
        }
    ]

    # Create map generator
    map_gen = MapGenerator()

    # Create before/after map
    comparison_map = map_gen.create_before_after_map(
        delivery_data, baseline_routes, optimized_routes, save_html=True
    )

    print("Map generation test completed successfully!")


if __name__ == "__main__":
    main()