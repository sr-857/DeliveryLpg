'use client'

import { useState, useEffect } from 'react'
import { Truck, MapPin, Navigation, Phone, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { getStatusColor } from '@/lib/utils'

interface Vehicle {
  id: string
  name: string
  registrationNumber: string
  driver: string
  driverPhone: string
  status: 'active' | 'idle' | 'maintenance' | 'offline'
  currentLocation?: {
    lat: number
    lng: number
    address: string
  }
  nextStop?: {
    customerName: string
    address: string
    eta: Date
  }
  route: {
    id: string
    totalDeliveries: number
    completedDeliveries: number
    totalDistance: number
    estimatedTime: number
  }
  fuelLevel: number
  fuelCapacity: number
  lastUpdate: Date
}

export function VehicleStatus() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([
    {
      id: 'vh001',
      name: 'Tanker Truck Alpha',
      registrationNumber: 'DL 01 CD 4521',
      driver: 'Rajesh Kumar',
      driverPhone: '+91 98765 43210',
      status: 'active',
      currentLocation: {
        lat: 28.6200,
        lng: 77.2100,
        address: 'Sector 15, Near Metro Station'
      },
      nextStop: {
        customerName: 'Gas Agency North',
        address: 'Sector 15, Block A, New Delhi',
        eta: new Date(Date.now() + 15 * 60000)
      },
      route: {
        id: 'r-2024-015',
        totalDeliveries: 4,
        completedDeliveries: 2,
        totalDistance: 42.3,
        estimatedTime: 180
      },
      fuelLevel: 65,
      fuelCapacity: 100,
      lastUpdate: new Date()
    },
    {
      id: 'vh002',
      name: 'Tanker Truck Beta',
      registrationNumber: 'DL 02 EF 6789',
      driver: 'Amit Singh',
      driverPhone: '+91 87654 32109',
      status: 'active',
      currentLocation: {
        lat: 28.6300,
        lng: 77.2200,
        address: 'Sector 45, Industrial Area'
      },
      nextStop: {
        customerName: 'Industrial Gas Supply',
        address: 'Sector 45, Plot 12, Gurugram',
        eta: new Date(Date.now() + 45 * 60000)
      },
      route: {
        id: 'r-2024-014',
        totalDeliveries: 3,
        completedDeliveries: 1,
        totalDistance: 25.7,
        estimatedTime: 120
      },
      fuelLevel: 40,
      fuelCapacity: 100,
      lastUpdate: new Date()
    },
    {
      id: 'vh003',
      name: 'Tanker Truck Gamma',
      registrationNumber: 'DL 03 GH 9876',
      driver: 'Suresh Patel',
      driverPhone: '+91 98765 54321',
      status: 'maintenance',
      route: {
        id: 'r-2024-016',
        totalDeliveries: 2,
        completedDeliveries: 2,
        totalDistance: 18.9,
        estimatedTime: 90
      },
      fuelLevel: 30,
      fuelCapacity: 100,
      lastUpdate: new Date(Date.now() - 30 * 60000)
    },
    {
      id: 'vh004',
      name: 'Tanker Truck Delta',
      registrationNumber: 'DL 04 IJ 5432',
      driver: 'Vikram Sharma',
      driverPhone: '+91 98765 65432',
      status: 'idle',
      lastUpdate: new Date(Date.now() - 10 * 60000)
    }
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setVehicles(prev => prev.map(vehicle => {
        // Update fuel levels
        const fuelChange = Math.random() > 0.8 ? -2 : Math.random() > 0.95 ? 1 : 0
        const newFuelLevel = Math.max(10, Math.min(95, vehicle.fuelLevel + fuelChange))

        // Update location for active vehicles
        if (vehicle.status === 'active') {
          const newLastUpdate = new Date()
          return {
            ...vehicle,
            fuelLevel: newFuelLevel,
            lastUpdate: newLastUpdate,
            // Simulate route progress
            ...(vehicle.route && {
              completedDeliveries: Math.min(
                vehicle.route.totalDeliveries,
                vehicle.route.completedDeliveries + (Math.random() > 0.7 ? 1 : 0)
              )
            })
          }
        }

        return vehicle
      }))
    }, 10000) // Update every 10 seconds

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <MapPin className="h-4 w-4 text-lime-500" />
      case 'idle':
        return <Navigation className="h-4 w-4 text-gray-500" />
      case 'maintenance':
        return <AlertTriangle className="h-4 w-4 text-amber-500" />
      default:
        return <Truck className="h-4 w-4 text-red-500" />
    }
  }

  const getFuelColor = (level: number) => {
    if (level > 70) return 'text-lime-600'
    if (level > 40) return 'text-amber-600'
    return 'text-red-600'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Vehicle Fleet Status</CardTitle>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-lime-500 text-lime-700">
            {vehicles.filter(v => v.status === 'active').length} Active
          </Badge>
          <Badge variant="outline" className="border-gray-500 text-gray-700">
            {vehicles.filter(v => v.status === 'idle').length} Idle
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="idle">Idle</TabsTrigger>
            <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {vehicles.map((vehicle) => (
              <div
                key={vehicle.id}
                className={`p-4 border rounded-lg ${
                  vehicle.status === 'active'
                    ? 'border-lime-500 bg-lime-50 dark:bg-lime-950'
                    : vehicle.status === 'idle'
                    ? 'border-gray-500 bg-gray-50 dark:bg-gray-950'
                    : vehicle.status === 'maintenance'
                    ? 'border-amber-500 bg-amber-50 dark:bg-amber-950'
                    : 'border-red-500 bg-red-50 dark:bg-red-950'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIcon(vehicle.status)}
                      <div>
                        <div className="font-semibold">{vehicle.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {vehicle.registrationNumber}
                        </div>
                      </div>
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    className={
                      vehicle.status === 'active'
                        ? 'border-lime-500 text-lime-700'
                        : vehicle.status === 'idle'
                        ? 'border-gray-500 text-gray-700'
                        : vehicle.status === 'maintenance'
                        ? 'border-amber-500 text-amber-700'
                        : 'border-red-500 text-red-700'
                    }
                  >
                    {vehicle.status === 'active' && 'Active'}
                    {vehicle.status === 'idle' && 'Idle'}
                    {vehicle.status === 'maintenance' && 'Maintenance'}
                    {vehicle.status === 'offline' && 'Offline'}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Driver:</span>
                    <span className="font-medium">{vehicle.driver}</span>
                  </div>

                  {vehicle.driverPhone && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Phone:</span>
                      <span className="font-medium">{vehicle.driverPhone}</span>
                    </div>
                  )}

                  {vehicle.currentLocation && (
                    <div className="flex items-start justify-between text-sm">
                      <span className="text-muted-foreground">Location:</span>
                      <span className="text-right text-xs text-muted-foreground">
                        {vehicle.currentLocation.address}
                      </span>
                    </div>
                  )}

                  {vehicle.nextStop && (
                    <div className="flex items-start justify-between text-sm">
                      <span className="text-muted-foreground">Next Stop:</span>
                      <div className="text-right text-xs text-muted-foreground">
                        <div>{vehicle.nextStop.customerName}</div>
                        <div>{vehicle.nextStop.address}</div>
                        <div className="text-xs text-lime-600">
                          ETA: {vehicle.nextStop.eta.toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  )}

                  {vehicle.route && (
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Route Progress:</span>
                        <span className="font-medium">
                          {vehicle.route.completedDeliveries}/{vehicle.route.totalDeliveries}
                        </span>
                      </div>
                      <Progress
                        value={
                          (vehicle.route.completedDeliveries / vehicle.route.totalDeliveries) * 100
                        }
                        className="h-2"
                      />
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Distance: {vehicle.route.totalDistance}km</span>
                        <span>Time: {vehicle.route.estimatedTime}min</span>
                    </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Fuel Level:</span>
                    <div className="flex items-center gap-2">
                      <div className={`font-medium ${getFuelColor(vehicle.fuelLevel)}`}>
                        {vehicle.fuelLevel}L
                      </div>
                      <span className="text-xs text-muted-foreground">
                        ({vehicle.fuelCapacity}L)
                      </span>
                      <Progress
                        value={(vehicle.fuelLevel / vehicle.fuelCapacity) * 100}
                        className="w-20 h-2"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Last Update:</span>
                    <span>{formatTime(vehicle.lastUpdate)}</span>
                  </div>
                </div>
              </div>
            ))}
          </TabsContent>

          <TabsContent value="active" className="space-y-4">
            {vehicles
              .filter(v => v.status === 'active')
              .map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="p-4 border-lime-500 bg-lime-50 dark:bg-lime-950 rounded-lg"
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-lime-500" />
                      <div>
                        <div className="font-semibold">{vehicle.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {vehicle.registrationNumber}
                        </div>
                      </div>
                    </div>
                    <Badge className="border-lime-500 text-lime-700">Active</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Driver: {vehicle.driver}
                  </div>
                  {vehicle.nextStop && (
                    <div className="text-sm">
                      <div className="font-medium text-foreground">
                        Next: {vehicle.nextStop.customerName}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {vehicle.nextStop.address}
                      </div>
                      <div className="text-xs text-lime-600">
                        ETA: {vehicle.nextStop.eta.toLocaleTimeString()}
                      </div>
                    </div>
                  )}
                </div>
              ))}
          </TabsContent>

          <TabsContent value="idle" className="space-y-4">
            {vehicles
              .filter(v => v.status === 'idle')
              .map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="p-4 border-gray-500 bg-gray-50 dark:bg-gray-950 rounded-lg"
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Navigation className="h-4 w-4 text-gray-500" />
                      <div>
                        <div className="font-semibold">{vehicle.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {vehicle.registrationNumber}
                        </div>
                      </div>
                    </div>
                    <Badge className="border-gray-500 text-gray-700">Idle</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Available for assignment
                  </div>
                </div>
              ))}
          </TabsContent>

          <TabsContent value="maintenance" className="space-y-4">
            {vehicles
              .filter(v => v.status === 'maintenance')
              .map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="p-4 border-amber-500 bg-amber-50 dark:bg-amber-950 rounded-lg"
                >
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      <div>
                        <div className="font-semibold">{vehicle.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {vehicle.registrationNumber}
                        </div>
                      </div>
                    </div>
                    <Badge className="border-amber-500 text-amber-700">Maintenance</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Scheduled maintenance in progress
                  </div>
                </div>
              ))}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}