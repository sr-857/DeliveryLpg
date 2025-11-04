'use client'

import { useState, useEffect } from 'react'
import { Calendar, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { motion } from 'framer-motion'
import { RouteMap } from '@/components/dashboard/route-map'
import { RecentDeliveries } from '@/components/dashboard/recent-deliveries'
import { SystemMetrics } from '@/components/dashboard/system-metrics'
import { VehicleStatus } from '@/components/dashboard/vehicle-status'

export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  // Mock data - in real app, this would come from API
  const stats = {
    totalDeliveries: {
      current: 247,
      previous: 232,
      trend: 6.5
    },
    activeVehicles: {
      current: 8,
      total: 10,
      status: 'active'
    },
    routeEfficiency: {
      current: 87,
      target: 90
    },
    fuelCost: {
      current: 45850,
      previous: 48230,
      trend: -4.9
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsRefreshing(false)
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Today's Overview</h1>
          <p className="text-muted-foreground">
            {selectedDate.toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSelectedDate(new Date())}
          >
            <Calendar className="h-4 w-4 mr-2" />
            Today
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Deliveries */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="stat-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Deliveries</CardTitle>
              <TrendingUp className="h-4 w-4 text-lime-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalDeliveries.current}</div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <span>+{stats.totalDeliveries.trend}% from yesterday</span>
                <div className="w-16 h-1 bg-lime-500 rounded-full" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Active Vehicles */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="stat-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Vehicles</CardTitle>
              <div className="w-2 h-2 bg-lime-500 rounded-full animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeVehicles.current}/{stats.activeVehicles.total}</div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <span className="text-lime-600">All vehicles operational</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Route Efficiency */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="stat-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Route Efficiency</CardTitle>
              <div className="w-6 h-6 bg-amber-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-amber-700">87%</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Progress value={stats.routeEfficiency.current} className="flex-1" />
                <span className="text-sm font-medium">{stats.routeEfficiency.current}%</span>
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Target: {stats.routeEfficiency.target}%
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Fuel Cost */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="stat-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Fuel Cost</CardTitle>
              <TrendingDown className="h-4 w-4 text-lime-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">₹{stats.fuelCost.current.toLocaleString()}</div>
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <span className="text-lime-600">-{Math.abs(stats.fuelCost.trend)}% from yesterday</span>
                <div className="w-16 h-1 bg-lime-500 rounded-full" />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="map">Map View</TabsTrigger>
          <TabsTrigger value="vehicles">Vehicles</TabsTrigger>
          <TabsTrigger value="deliveries">Deliveries</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RouteMap className="h-[400px]" />
            <div className="space-y-6">
              <SystemMetrics />
              <VehicleStatus />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="map" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Live Route Map</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <RouteMap className="h-[600px]" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vehicles" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Vehicle Fleet Status</CardTitle>
            </CardHeader>
            <CardContent>
              <VehicleStatus />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="deliveries" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Deliveries</CardTitle>
            </CardHeader>
            <CardContent>
              <RecentDeliveries />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}