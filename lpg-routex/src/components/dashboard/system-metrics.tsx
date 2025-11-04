'use client'

import { useState, useEffect } from 'react'
import { Truck, Fuel, TrendingUp, Users, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'

interface SystemMetrics {
  uptime: number
  totalRequests: number
  successRate: number
  averageResponseTime: number
  activeUsers: number
  systemLoad: number
}

export function SystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    uptime: 99.7,
    totalRequests: 1247,
    successRate: 98.3,
    averageResponseTime: 245,
    activeUsers: 8,
    systemLoad: 65
  })

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        uptime: Math.min(99.9, prev.uptime + (Math.random() * 0.1)),
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 3),
        successRate: Math.min(99.9, prev.successRate + (Math.random() - 0.5)),
        averageResponseTime: Math.max(200, prev.averageResponseTime + (Math.random() * 20 - 10)),
        activeUsers: prev.activeUsers + (Math.random() > 0.7 ? 1 : Math.random() > 0.9 ? -1 : 0),
        systemLoad: Math.max(30, Math.min(90, prev.systemLoad + (Math.random() * 10 - 5)))
      }))
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {/* System Uptime */}
      <Card className="stat-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-lime-500" />
            <span className="text-xs text-lime-600">Live</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold">{metrics.uptime}%</div>
            <div className="text-xs text-muted-foreground">
              Running for {Math.floor(metrics.uptime * 24)} hours
            </div>
          </div>
          <Progress value={metrics.uptime} className="mt-2" />
        </CardContent>
      </Card>

      {/* API Performance */}
      <Card className="stat-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">API Performance</CardTitle>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-lime-500" />
            <span className="text-xs text-lime-600">Good</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Success Rate:</span>
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{metrics.successRate}%</span>
                <Badge
                  variant="outline"
                  className={metrics.successRate > 95 ? 'border-lime-500 text-lime-700' : ''}
                >
                  {metrics.successRate > 95 ? 'Excellent' : 'Good'}
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Response Time:</span>
              <span className="font-medium text-sm">{metrics.averageResponseTime}ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Requests:</span>
              <span className="font-medium text-sm">{metrics.totalRequests}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Active Users */}
      <Card className="stat-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Users</CardTitle>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-lime-500" />
            <span className="text-xs text-lime-600">Now</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold">{metrics.activeUsers}</div>
            <div className="text-xs text-muted-foreground">
              Online drivers
            </div>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            Peak: 10 users at 2:00 PM
          </div>
        </CardContent>
      </Card>

      {/* System Load */}
      <Card className="stat-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">System Load</CardTitle>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500"
                style={{ width: `${metrics.systemLoad}%` }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{metrics.systemLoad}%</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">CPU:</span>
              <span className="font-medium">{Math.floor(metrics.systemLoad * 0.6)}%</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Memory:</span>
              <span className="font-medium">{Math.floor(metrics.systemLoad * 0.4)}%</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Disk:</span>
              <span className="font-medium">{Math.floor(metrics.systemLoad * 0.2)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Fuel Efficiency */}
      <Card className="stat-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Today's Efficiency</CardTitle>
          <div className="flex items-center gap-2">
            <Fuel className="h-4 w-4 text-lime-500" />
            <span className="text-xs text-lime-600">Optimal</span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Fuel Saved:</span>
              <span className="font-medium text-lime-600">234 L</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">CO₂ Reduced:</span>
              <span className="font-medium text-lime-600">324 kg</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Efficiency:</span>
              <div className="flex items-center gap-2">
                <span className="font-medium text-lime-600">87%</span>
                <Badge
                  variant="outline"
                  className="border-lime-500 text-lime-700"
                >
                  +3% vs target
                </Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}