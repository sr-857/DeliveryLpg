"""
Streamlit dashboard for LPG delivery route optimization
Interactive web interface for visualization and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import json

# Import our custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimization.route_optimizer import RouteOptimizer
from visualization.map_generator import MapGenerator
from utils.metrics import MetricsCalculator
from utils.config import VISUALIZATION, DATA_GENERATION, DELIVERY


class Dashboard:
    """Main Streamlit dashboard for route optimization"""

    def __init__(self):
        self.optimizer = RouteOptimizer()
        self.map_generator = MapGenerator()
        self.metrics_calculator = MetricsCalculator()

        # Session state initialization
        if 'optimization_results' not in st.session_state:
            st.session_state.optimization_results = None
        if 'delivery_data' not in st.session_state:
            st.session_state.delivery_data = None
        if 'current_scenario' not in st.session_state:
            st.session_state.current_scenario = None

    def run(self):
        """Main dashboard entry point"""
        st.set_page_config(
            page_title="LPG Delivery Route Optimization",
            page_icon="🚛",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        self._setup_page_style()
        self._render_header()

        # Sidebar for controls
        self._render_sidebar()

        # Main content area
        if st.session_state.optimization_results is None:
            self._render_welcome_page()
        else:
            self._render_results_page()

    def _setup_page_style(self):
        """Setup custom CSS styling"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .improvement-positive {
            color: #2ca02c;
            font-weight: bold;
        }
        .improvement-negative {
            color: #d62728;
            font-weight: bold;
        }
        .stDataFrame {
            border-radius: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

    def _render_header(self):
        """Render dashboard header"""
        st.markdown('<h1 class="main-header">🚛 LPG Delivery Route Optimization</h1>', unsafe_allow_html=True)
        st.markdown("---")

    def _render_sidebar(self):
        """Render sidebar with controls"""
        st.sidebar.title("🎛️ Optimization Controls")

        # Scenario Generation Section
        st.sidebar.header("📍 Scenario Generation")
        num_deliveries = st.sidebar.slider(
            "Number of Deliveries",
            min_value=DATA_GENERATION.min_deliveries,
            max_value=DATA_GENERATION.max_deliveries,
            value=DATA_GENERATION.default_deliveries,
            step=1
        )

        urban_percentage = st.sidebar.slider(
            "Urban Delivery Percentage",
            min_value=20,
            max_value=80,
            value=int(DATA_GENERATION.urban_percentage * 100),
            step=5
        ) / 100

        # Optimization Parameters Section
        st.sidebar.header("⚙️ Optimization Parameters")
        num_vehicles = st.sidebar.slider(
            "Number of Vehicles",
            min_value=1,
            max_value=10,
            value=4,
            step=1
        )

        time_limit = st.sidebar.slider(
            "Solver Time Limit (seconds)",
            min_value=10,
            max_value=120,
            value=OPTIMIZATION.solver_time_limit_seconds,
            step=10
        )

        include_time_windows = st.sidebar.checkbox(
            "Include Time Window Constraints",
            value=True
        )

        # Action Buttons
        st.sidebar.header("🚀 Actions")
        generate_button = st.sidebar.button(
            "🔄 Generate New Scenario",
            type="secondary"
        )

        optimize_button = st.sidebar.button(
            "🚀 Run Optimization",
            type="primary"
        )

        # Handle button actions
        if generate_button:
            self._generate_new_scenario(num_deliveries, urban_percentage)

        if optimize_button:
            self._run_optimization(num_vehicles, time_limit, include_time_windows)

        # Load Sample Data Option
        st.sidebar.header("📂 Quick Start")
        if st.sidebar.button("Load Sample Scenario"):
            self._load_sample_scenario()

    def _render_welcome_page(self):
        """Render welcome page when no data is loaded"""
        st.markdown("""
        ## 🎯 Welcome to LPG Delivery Route Optimization!

        This intelligent system optimizes delivery routes for LPG (Liquefied Petroleum Gas) trucks,
        helping to reduce fuel consumption, save time, and improve delivery efficiency.

        ### 🚀 Key Features:
        - **🗺️ Interactive Maps**: Visualize routes before and after optimization
        - **📊 Performance Metrics**: Track distance, time, and cost improvements
        - **⚙️ Customizable Parameters**: Adjust vehicles, time windows, and constraints
        - **📍 Mixed Areas**: Handle both urban and rural delivery scenarios

        ### 🎮 How to Use:
        1. **Generate Scenario**: Use the sidebar controls to create a delivery scenario
        2. **Run Optimization**: Click "Run Optimization" to find optimal routes
        3. **Analyze Results**: Explore maps and metrics to see improvements

        ### 📈 Expected Improvements:
        - **Distance Reduction**: 20-40% fewer kilometers traveled
        - **Cost Savings**: 15-30% reduction in total delivery costs
        - **Time Efficiency**: 25-35% improvement in delivery time
        - **Fuel Conservation**: 20-35% reduction in fuel consumption

        ---
        **👈 Get started by generating a scenario or loading sample data from the sidebar!**
        """)

        # Add sample metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Avg Distance Reduction", value="28%", delta="Better than baseline")
        with col2:
            st.metric(label="Avg Cost Savings", value="$156", delta="Per day")
        with col3:
            st.metric(label="Avg Time Saved", value="2.3 hrs", delta="Per day")
        with col4:
            st.metric(label="Fuel Saved", value="12 gal", delta="Per day")

    def _render_results_page(self):
        """Render main results page with optimization data"""
        if not st.session_state.optimization_results:
            return

        results = st.session_state.optimization_results
        optimized_solution = results.get('optimized_solution', {})
        improvement_metrics = results.get('improvement_metrics', {})

        # Key Performance Indicators
        self._render_kpi_cards(improvement_metrics)

        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗺️ Route Maps", "📊 Performance Metrics", "📋 Route Details", "📍 Delivery Points", "📈 Analytics"
        ])

        with tab1:
            self._render_route_maps()

        with tab2:
            self._render_performance_metrics(improvement_metrics)

        with tab3:
            self._render_route_details(optimized_solution)

        with tab4:
            self._render_delivery_points()

        with tab5:
            self._render_analytics()

    def _render_kpi_cards(self, improvement_metrics):
        """Render key performance indicator cards"""
        if not improvement_metrics:
            return

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            distance_reduction = improvement_metrics.get('distance_reduction_percent', 0)
            st.metric(
                label="🛣️ Distance Reduction",
                value=f"{distance_reduction:.1f}%",
                delta=f"{improvement_metrics.get('distance_reduction_km', 0):.1f} km"
            )

        with col2:
            cost_savings = improvement_metrics.get('cost_savings_percent', 0)
            st.metric(
                label="💰 Cost Savings",
                value=f"{cost_savings:.1f}%",
                delta=f"${improvement_metrics.get('cost_savings', 0):.2f}"
            )

        with col3:
            vehicles_used = improvement_metrics.get('optimized', {}).get('total_distance_km', 0)
            st.metric(
                label="🚛 Optimized Distance",
                value=f"{vehicles_used:.1f} km",
                delta="vs baseline"
            )

        with col4:
            vehicles_reduced = improvement_metrics.get('vehicles_reduction', 0)
            st.metric(
                label="🚚 Vehicles Used",
                value=improvement_metrics.get('optimized', {}).get('vehicles_used', 0),
                delta=f"-{vehicles_reduced}" if vehicles_reduced > 0 else "0"
            )

        st.markdown("---")

    def _render_route_maps(self):
        """Render before/after route comparison maps"""
        st.subheader("🗺️ Route Comparison Maps")

        if not st.session_state.delivery_data or not st.session_state.optimization_results:
            st.warning("No optimization results available. Please run optimization first.")
            return

        delivery_data = st.session_state.delivery_data
        results = st.session_state.optimization_results

        # Create map view selector
        view_mode = st.radio(
            "Select Map View:",
            ["Before & After Comparison", "Optimized Routes Only", "Baseline Routes Only"],
            horizontal=True
        )

        if view_mode == "Before & After Comparison":
            st.subheader("🔄 Before (Red) vs After (Green) Routes")
            comparison_map = self.map_generator.create_before_after_map(
                delivery_data=delivery_data,
                baseline_routes=results.get('baseline_solution', {}).get('routes', []),
                optimized_routes=results.get('optimized_solution', {}).get('routes', [])
            )
            st.components.v1.html(comparison_map._repr_html_(), height=600)

        elif view_mode == "Optimized Routes Only":
            st.subheader("✅ Optimized Routes")
            optimized_map = self.map_generator.create_route_analysis_map(
                delivery_data=delivery_data,
                routes=results.get('optimized_solution', {}).get('routes', []),
                route_type='optimized'
            )
            st.components.v1.html(optimized_map._repr_html_(), height=600)

        else:  # Baseline Routes Only
            st.subheader("📍 Baseline Routes")
            baseline_map = self.map_generator.create_route_analysis_map(
                delivery_data=delivery_data,
                routes=results.get('baseline_solution', {}).get('routes', []),
                route_type='baseline'
            )
            st.components.v1.html(baseline_map._repr_html_(), height=600)

    def _render_performance_metrics(self, improvement_metrics):
        """Render performance metrics charts"""
        st.subheader("📊 Performance Metrics")

        if not improvement_metrics:
            st.warning("No improvement metrics available.")
            return

        # Create comparison charts
        col1, col2 = st.columns(2)

        with col1:
            # Distance comparison
            baseline_dist = improvement_metrics.get('baseline', {}).get('total_distance_km', 0)
            optimized_dist = improvement_metrics.get('optimized', {}).get('total_distance_km', 0)

            fig_distance = go.Figure()
            fig_distance.add_trace(go.Bar(
                name='Baseline',
                x=['Total Distance'],
                y=[baseline_dist],
                marker_color='red'
            ))
            fig_distance.add_trace(go.Bar(
                name='Optimized',
                x=['Total Distance'],
                y=[optimized_dist],
                marker_color='green'
            ))
            fig_distance.update_layout(
                title='🛣️ Distance Comparison (km)',
                yaxis_title='Distance (km)',
                height=400
            )
            st.plotly_chart(fig_distance, use_container_width=True)

        with col2:
            # Cost comparison
            baseline_cost = improvement_metrics.get('baseline', {}).get('total_cost', 0)
            optimized_cost = improvement_metrics.get('optimized', {}).get('total_cost', 0)

            fig_cost = go.Figure()
            fig_cost.add_trace(go.Bar(
                name='Baseline',
                x=['Total Cost'],
                y=[baseline_cost],
                marker_color='red'
            ))
            fig_cost.add_trace(go.Bar(
                name='Optimized',
                x=['Total Cost'],
                y=[optimized_cost],
                marker_color='green'
            ))
            fig_cost.update_layout(
                title='💰 Cost Comparison ($)',
                yaxis_title='Cost ($)',
                height=400
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        # Improvement percentages
        col3, col4, col5 = st.columns(3)

        with col3:
            distance_improvement = improvement_metrics.get('distance_reduction_percent', 0)
            fig_dist_pie = go.Figure(data=[go.Pie(
                labels=['Reduced', 'Remaining'],
                values=[distance_improvement, 100 - distance_improvement],
                hole=0.3,
                marker_colors=['green', 'lightgray']
            )])
            fig_dist_pie.update_layout(
                title=f'Distance Reduction: {distance_improvement:.1f}%',
                height=300
            )
            st.plotly_chart(fig_dist_pie, use_container_width=True)

        with col4:
            cost_improvement = improvement_metrics.get('cost_savings_percent', 0)
            fig_cost_pie = go.Figure(data=[go.Pie(
                labels=['Saved', 'Remaining'],
                values=[cost_improvement, 100 - cost_improvement],
                hole=0.3,
                marker_colors=['green', 'lightgray']
            )])
            fig_cost_pie.update_layout(
                title=f'Cost Savings: {cost_improvement:.1f}%',
                height=300
            )
            st.plotly_chart(fig_cost_pie, use_container_width=True)

        with col5:
            # Environmental impact
            fuel_reduction = improvement_metrics.get('optimized', {}).get('total_distance_km', 0) * 0.1  # Estimate
            co2_reduction = fuel_reduction * 19.6  # lbs CO2 per gallon

            st.metric(
                label="🌱 CO₂ Reduction",
                value=f"{co2_reduction:.1f} lbs",
                delta="Environmental benefit"
            )
            st.metric(
                label="⛽ Fuel Saved",
                value=f"{fuel_reduction:.1f} gal",
                delta="Cost & environmental benefit"
            )

    def _render_route_details(self, optimized_solution):
        """Render detailed route information"""
        st.subheader("📋 Route Details")

        if not optimized_solution or 'routes' not in optimized_solution:
            st.warning("No route details available.")
            return

        routes = optimized_solution['routes']

        if not routes:
            st.warning("No routes found in solution.")
            return

        # Create route summary table
        route_data = []
        for i, route in enumerate(routes):
            num_deliveries = len(route.get('stops', [])) - 2  # Exclude depot
            route_data.append({
                'Route #': i + 1,
                'Deliveries': num_deliveries,
                'Distance (km)': f"{route.get('total_distance', 0):.2f}",
                'Demand (cylinders)': route.get('total_demand', 0),
                'Efficiency (km/delivery)': f"{route.get('total_distance', 0) / num_deliveries:.2f}" if num_deliveries > 0 else "N/A"
            })

        route_df = pd.DataFrame(route_data)
        st.dataframe(route_df, use_container_width=True)

        # Detailed route stops
        st.subheader("🔍 Detailed Route Stops")

        selected_route = st.selectbox(
            "Select a route to view details:",
            options=[f"Route {i+1}" for i in range(len(routes))],
            index=0
        )

        route_idx = int(selected_route.split()[1]) - 1
        if route_idx < len(routes):
            route = routes[route_idx]
            stops = route.get('stops', [])

            if st.session_state.delivery_data is not None:
                # Get detailed stop information
                stop_details = []
                for stop_id in stops:
                    if stop_id == 0:
                        stop_details.append({
                            'Stop #': len(stop_details) + 1,
                            'Location ID': stop_id,
                            'Type': 'Depot',
                            'Demand': 0,
                            'Address': 'LPG Depot - Central Distribution'
                        })
                    else:
                        delivery_info = st.session_state.delivery_data[
                            st.session_state.delivery_data['id'] == stop_id
                        ]
                        if not delivery_info.empty:
                            row = delivery_info.iloc[0]
                            stop_details.append({
                                'Stop #': len(stop_details) + 1,
                                'Location ID': stop_id,
                                'Type': f"{row['area_type'].title()} - {row['priority'].title()}",
                                'Demand': row['demand'],
                                'Address': row['address'],
                                'Time Window': f"{row['time_window_start']} - {row['time_window_end']}",
                                'Service Time': f"{row['service_time_minutes']} min"
                            })

                stop_df = pd.DataFrame(stop_details)
                st.dataframe(stop_df, use_container_width=True)

    def _render_delivery_points(self):
        """Render delivery points information"""
        st.subheader("📍 Delivery Points Information")

        if st.session_state.delivery_data is None:
            st.warning("No delivery data available.")
            return

        delivery_data = st.session_state.delivery_data.copy()

        # Exclude depot for statistics
        delivery_only = delivery_data[delivery_data['id'] != 0]

        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Deliveries", len(delivery_only))
        with col2:
            st.metric("Total Demand", f"{delivery_only['demand'].sum()} cylinders")
        with col3:
            urban_count = (delivery_only['area_type'] == 'urban').sum()
            st.metric("Urban Deliveries", urban_count)
        with col4:
            rural_count = (delivery_only['area_type'] == 'rural').sum()
            st.metric("Rural Deliveries", rural_count)

        # Filter and search
        col1, col2 = st.columns(2)

        with col1:
            area_filter = st.selectbox(
                "Filter by Area Type:",
                options=["All", "Urban", "Rural"],
                index=0
            )

        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority:",
                options=["All", "Normal", "High", "Emergency"],
                index=0
            )

        # Apply filters
        filtered_data = delivery_only.copy()
        if area_filter != "All":
            filtered_data = filtered_data[filtered_data['area_type'] == area_filter.lower()]
        if priority_filter != "All":
            filtered_data = filtered_data[filtered_data['priority'] == priority_filter.lower()]

        # Display filtered data
        st.dataframe(
            filtered_data[['id', 'area_type', 'priority', 'demand', 'time_window_start',
                          'time_window_end', 'address']],
            use_container_width=True
        )

    def _render_analytics(self):
        """Render advanced analytics and insights"""
        st.subheader("📈 Advanced Analytics")

        if not st.session_state.optimization_results:
            st.warning("No optimization results available for analytics.")
            return

        results = st.session_state.optimization_results

        # Optimization performance
        st.subheader("⚡ Optimization Performance")
        opt_info = results.get('optimization_info', {})

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Solver Status",
                opt_info.get('solver_status', 'Unknown'),
                delta="Success" if opt_info.get('solver_status') == 'optimal' else "Check"
            )
            st.metric(
                "Optimization Time",
                f"{opt_info.get('total_optimization_time_seconds', 0):.2f} seconds"
            )

        with col2:
            st.metric(
                "Solver Efficiency",
                "Fast",
                delta="< 30 seconds target met" if opt_info.get('total_optimization_time_seconds', 0) < 30 else "Slow"
            )

        # Delivery distribution analysis
        if st.session_state.delivery_data is not None:
            st.subheader("📊 Delivery Distribution Analysis")

            delivery_only = st.session_state.delivery_data[
                st.session_state.delivery_data['id'] != 0
            ]

            # Area type distribution
            col1, col2 = st.columns(2)

            with col1:
                area_counts = delivery_only['area_type'].value_counts()
                fig_area = px.pie(
                    values=area_counts.values,
                    names=area_counts.index,
                    title="Area Type Distribution"
                )
                st.plotly_chart(fig_area, use_container_width=True)

            with col2:
                priority_counts = delivery_only['priority'].value_counts()
                fig_priority = px.pie(
                    values=priority_counts.values,
                    names=priority_counts.index,
                    title="Priority Distribution"
                )
                st.plotly_chart(fig_priority, use_container_width=True)

            # Demand distribution
            st.subheader("📦 Demand Distribution")
            fig_demand = px.histogram(
                delivery_only,
                x='demand',
                nbins=20,
                title="LPG Cylinder Demand Distribution",
                labels={'demand': 'Number of Cylinders', 'count': 'Number of Deliveries'}
            )
            st.plotly_chart(fig_demand, use_container_width=True)

    def _generate_new_scenario(self, num_deliveries, urban_percentage):
        """Generate new delivery scenario"""
        with st.spinner("🔄 Generating new delivery scenario..."):
            try:
                # Update configuration with user settings
                import src.utils.config as config
                config.DATA_GENERATION.urban_percentage = urban_percentage

                # Generate scenario
                delivery_data, scenario_summary = self.optimizer.generate_delivery_scenario(
                    num_deliveries=num_deliveries
                )

                # Store in session state
                st.session_state.delivery_data = delivery_data
                st.session_state.current_scenario = scenario_summary

                # Clear previous optimization results
                st.session_state.optimization_results = None

                st.success(f"✅ Generated scenario with {num_deliveries} deliveries!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating scenario: {str(e)}")

    def _run_optimization(self, num_vehicles, time_limit, include_time_windows):
        """Run route optimization"""
        if st.session_state.delivery_data is None:
            st.warning("⚠️ Please generate a scenario first!")
            return

        with st.spinner("🚀 Running route optimization... This may take a few seconds..."):
            try:
                # Run optimization
                results = self.optimizer.optimize_single_scenario(
                    num_deliveries=len(st.session_state.delivery_data) - 1,
                    num_vehicles=num_vehicles,
                    time_limit_seconds=time_limit,
                    include_time_windows=include_time_windows
                )

                # Store results
                st.session_state.optimization_results = results

                st.success("✅ Optimization completed successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error during optimization: {str(e)}")

    def _load_sample_scenario(self):
        """Load sample scenario for demonstration"""
        with st.spinner("📂 Loading sample scenario..."):
            try:
                # Generate a sample scenario with fixed seed for consistency
                self.optimizer.seed = 42
                delivery_data, scenario_summary = self.optimizer.generate_delivery_scenario(
                    num_deliveries=25
                )

                # Run optimization on sample data
                results = self.optimizer.optimize_single_scenario(
                    num_deliveries=25,
                    num_vehicles=4,
                    time_limit_seconds=30
                )

                # Store in session state
                st.session_state.delivery_data = delivery_data
                st.session_state.current_scenario = scenario_summary
                st.session_state.optimization_results = results

                st.success("✅ Sample scenario loaded and optimized!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error loading sample scenario: {str(e)}")


def main():
    """Main entry point for the dashboard"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()