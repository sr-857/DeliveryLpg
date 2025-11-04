'use client'

import { useState, useEffect } from 'react'
import { MapPin, Navigation, ZoomIn, ZoomOut, Layers, Activity } from 'lucide-react'
import { Card } from '@/components/ui/card'

interface MapMarker {
  id: string
  lat: number
  lng: number
  type: 'depot' | 'delivery' | 'current'
  label: string
  status: 'completed' | 'in-progress' | 'pending'
  estimatedTime?: Date
}

export function RouteMap({ className }: { className?: string }) {
  const [mapStyle, setMapStyle] = useState('mapbox://styles/v1')
  const [center, setCenter] = useState({ lat: 28.6139, lng: 77.2090 })
  const [zoom, setZoom] = useState(12)
  const [markers, setMarkers] = useState<MapMarker[]>([
    {
      id: 'depot',
      lat: 28.6139,
      lng: 77.2090,
      type: 'depot',
      label: 'Main Depot',
      status: 'completed'
    },
    {
      id: '1',
      lat: 28.6200,
      lng: 77.2100,
      type: 'delivery',
      label: 'Delivery #1: Sector 15',
      status: 'completed',
      estimatedTime: new Date(Date.now() - 30 * 60000)
    },
    {
      id: '2',
      lat: 28.6300,
      lng: 77.2200,
      type: 'delivery',
      label: 'Delivery #2: Sector 45',
      status: 'completed',
      estimatedTime: new Date(Date.now() - 15 * 60000)
    },
    {
      id: '3',
      lat: 28.6400,
      lng: 77.2000,
      type: 'delivery',
      label: 'Delivery #3: Sector 72',
      status: 'in-progress',
      estimatedTime: new Date(Date.now() + 10 * 60000)
    },
    {
      id: '4',
      lat: 28.6150,
      lng: 77.1950,
      type: 'delivery',
      label: 'Delivery #4: Sector 22',
      status: 'pending',
      estimatedTime: new Date(Date.now() + 30 * 60000)
    }
  ])

  const routes = [
    {
      id: 'route-1',
      coordinates: [
        [77.2090, 28.6139], // depot
        [77.2100, 28.6200], // delivery 1
        [77.2200, 28.6300], // delivery 2
        [77.2000, 28.6400], // delivery 3
        [77.2090, 28.6139], // back to depot
      ],
      color: '#66BB6A', // lime green
      vehicleId: 'vehicle-1'
    },
    {
      id: 'route-2',
      coordinates: [
        [77.2090, 28.6139], // depot
        [77.1950, 28.6150], // delivery 4
        [77.2090, 28.6139], // back to depot
      ],
      color: '#FF9500', // orange
      vehicleId: 'vehicle-2'
    }
  ]

  return (
    <Card className={className}>
      <div className="relative h-full w-full">
        {/* Map Placeholder */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-lime-50 opacity-50">
          {/* This would be replaced with actual map component */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                <MapPin className="h-8 w-8 text-primary" />
              </div>
              <p className="text-lg font-semibold text-foreground">
                Interactive Map
              </p>
              <p className="text-sm text-muted-foreground">
                Real-time route visualization
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <div className="w-3 h-3 bg-lime-500 rounded-full"></div>
                <span>Active: {markers.filter(m => m.status === 'in-progress').length}</span>
                <span>•</span>
                <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                <span>Idle: {markers.filter(m => m.status === 'pending').length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Map Controls */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg border p-2 space-y-2">
          <div className="flex gap-2">
            <button
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              onClick={() => setZoom(Math.min(zoom + 1, 20))}
            >
              <ZoomIn className="h-4 w-4" />
            </button>
            <button
              className="p-2 hover:bg-gray-100 rounded transition-colors"
              onClick={() => setZoom(Math.max(zoom - 1, 8))}
            >
              <ZoomOut className="h-4 w-4" />
            </button>
          </div>
          <div className="flex gap-2">
            <button className="p-2 hover:bg-gray-100 rounded transition-colors">
              <Layers className="h-4 w-4" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded transition-colors">
              <Activity className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Vehicle Legend */}
        <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg border p-4">
          <h4 className="font-semibold text-sm mb-2">Active Vehicles</h4>
          <div className="space-y-2">
            {routes.map((route) => (
              <div key={route.id} className="flex items-center gap-2 text-sm">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: route.color }}
                />
                <span>Vehicle #{route.vehicleId.split('-')[1]}</span>
                <Badge
                  variant="outline"
                  className={route.vehicleId === 'vehicle-1' ? 'border-lime-500 text-lime-700' : ''}
                >
                  {route.vehicleId === 'vehicle-1' ? 'Active' : 'Idle'}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Delivery Status Legend */}
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg border p-4">
          <h4 className="font-semibold text-sm mb-2">Delivery Status</h4>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 bg-lime-500 rounded-full"></div>
              <span>Completed</span>
              <span className="text-xs text-muted-foreground">
                ({markers.filter(m => m.status === 'completed').length})
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 bg-amber-500 rounded-full animate-pulse"></div>
              <span>In Progress</span>
              <span className="text-xs text-muted-foreground">
                ({markers.filter(m => m.status === 'in-progress').length})
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span>Pending</span>
              <span className="text-xs text-muted-foreground">
                ({markers.filter(m => m.status === 'pending').length})
              </span>
            </div>
          </div>
        </div>

        {/* Route Information */}
        <div className="absolute top-20 right-4 bg-white rounded-lg shadow-lg border p-4 max-w-xs">
          <h4 className="font-semibold text-sm mb-2">Route Statistics</h4>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Distance:</span>
              <span className="font-medium">42.3 km</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Active Routes:</span>
              <span className="font-medium">2</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total Deliveries:</span>
              <span className="font-medium">4</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Efficiency:</span>
              <span className="font-medium text-lime-600">87%</span>
            </div>
          </div>
        </div>

        {/* Route Lines (Mock implementation) */}
        <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 1 }}>
          {routes.map((route) => (
            <g key={route.id}>
              {route.coordinates.map((coord, index) => {
                if (index === 0) return null
                return (
                  <line
                    key={index}
                    x1={route.coordinates[index - 1][0]}
                    y1={route.coordinates[index - 1][1]}
                    x2={coord[0]}
                    y2={coord[1]}
                    stroke={route.color}
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray="8,4"
                    className="animate-pulse"
                  />
                )
              })}
            </g>
          ))}
        </svg>
      </div>
    </Card>
  )
}