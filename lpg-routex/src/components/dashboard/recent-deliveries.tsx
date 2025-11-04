'use client'

import { useState, useEffect } from 'react'
import { Clock, CheckCircle, AlertCircle, MoreHorizontal } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatTime, formatRelativeTime, getStatusColor, getStatusBgColor } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Delivery {
  id: string
  vehicleId: string
  driver: string
  routeId: string
  status: 'on-time' | 'delayed' | 'failed'
  eta?: Date
  delayReason?: string
  customerName: string
  address: string
  quantity: number
  fuelConsumed: number
  completedAt?: Date
}

export function RecentDeliveries() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([
    {
      id: '1',
      vehicleId: 'VH-001',
      driver: 'Rajesh Kumar',
      routeId: 'R-2024-015',
      status: 'on-time',
      eta: new Date(Date.now() + 15 * 60000),
      customerName: 'Gas Agency North',
      address: 'Sector 15, Block A, New Delhi',
      quantity: 5,
      fuelConsumed: 12.5,
    },
    {
      id: '2',
      vehicleId: 'VH-002',
      driver: 'Amit Singh',
      routeId: 'R-2024-014',
      status: 'delayed',
      eta: new Date(Date.now() + 45 * 60000),
      delayReason: 'Traffic congestion',
      customerName: 'Industrial Gas Supply',
      address: 'Sector 45, Plot 12, Gurugram',
      quantity: 8,
      fuelConsumed: 18.2,
    },
    {
      id: '3',
      vehicleId: 'VH-003',
      driver: 'Suresh Patel',
      routeId: 'R-2024-016',
      status: 'failed',
      customerName: 'Commercial Gas Co.',
      address: 'Sector 72, Building 5, Saket',
      quantity: 3,
      fuelConsumed: 8.7,
      completedAt: new Date(Date.now() - 2 * 3600000),
    },
    {
      id: '4',
      vehicleId: 'VH-001',
      driver: 'Rajesh Kumar',
      routeId: 'R-2024-017',
      status: 'on-time',
      customerName: 'Residential Complex A',
      address: 'Sector 22, Tower 3, Rohini',
      quantity: 6,
      fuelConsumed: 15.3,
      completedAt: new Date(Date.now() - 1 * 3600000),
    },
    {
      id: '5',
      vehicleId: 'VH-004',
      driver: 'Vikram Sharma',
      routeId: 'R-2024-013',
      status: 'on-time',
      eta: new Date(Date.now() + 5 * 60000),
      customerName: 'Restaurant Row',
      address: 'Connaught Place, Block C',
      quantity: 4,
      fuelConsumed: 9.8,
    },
  ])

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setDeliveries(prev => prev.map(delivery => {
        if (delivery.status === 'on-time' && delivery.eta) {
          const newEta = new Date(delivery.eta.getTime() - 60000) // Decrease by 1 minute
          if (newEta < new Date()) {
            return {
              ...delivery,
              status: 'completed',
              completedAt: new Date(),
              eta: undefined
            }
          }
          return { ...delivery, eta: newEta }
        }
        if (delivery.status === 'delayed' && delivery.eta) {
          const newEta = new Date(delivery.eta.getTime() + 30000) // Increase by 30 seconds
          if (newEta > new Date(Date.now() + 2 * 3600000)) {
            return {
              ...delivery,
              status: 'failed',
              eta: undefined
            }
          }
          return { ...delivery, eta: newEta }
        }
        return delivery
      }))
    }, 30000) // Update every 30 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Deliveries</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Vehicle</TableHead>
              <TableHead>Driver</TableHead>
              <TableHead>Route</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>ETA</TableHead>
              <TableHead>Delay</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {deliveries.map((delivery) => (
              <TableRow key={delivery.id} className="hover:bg-accent/50">
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{delivery.vehicleId}</span>
                    <Badge
                      variant="outline"
                      className={
                        delivery.status === 'on-time'
                          ? 'border-lime-500 text-lime-700'
                          : delivery.status === 'delayed'
                          ? 'border-amber-500 text-amber-700'
                          : 'border-red-500 text-red-700'
                      }
                    >
                      {delivery.status === 'on-time' ? 'On-time' : delivery.status === 'delayed' ? 'Delayed' : 'Failed'}
                    </Badge>
                  </div>
                </TableCell>
                <TableCell>{delivery.driver}</TableCell>
                <TableCell>
                  <div>
                    <span className="font-medium">{delivery.routeId}</span>
                    <div className="text-xs text-muted-foreground">
                      {delivery.quantity} LPG cylinders
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={getStatusBgColor(delivery.status)}
                  >
                    {delivery.status === 'on-time' && 'On-time'}
                    {delivery.status === 'delayed' && 'Delayed'}
                    {delivery.status === 'failed' && 'Failed'}
                  </Badge>
                </TableCell>
                <TableCell>
                  {delivery.eta ? (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{formatTime(delivery.eta)}</span>
                    </div>
                  ) : delivery.completedAt ? (
                    <span className="text-muted-foreground">
                      {formatRelativeTime(delivery.completedAt)}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">-</span>
                  )}
                </TableCell>
                <TableCell>
                  {delivery.delayReason && (
                    <Badge
                      variant="outline"
                      className="border-amber-500 text-amber-700"
                    >
                      {delivery.delayReason}
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        Track Vehicle
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        Contact Driver
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}