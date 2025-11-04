'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Route,
  MapPin,
  Map,
  BarChart3,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { motion } from 'framer-motion'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: 'Route Planner',
    href: '/planner',
    icon: Route,
    badge: null,
  },
  {
    name: 'Live Tracking',
    href: '/tracking',
    icon: MapPin,
    badge: 'Live',
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    badge: null,
  },
  {
    name: 'Admin Panel',
    href: '/admin',
    icon: Settings,
    badge: null,
  },
  {
    name: 'Support',
    href: '/support',
    icon: HelpCircle,
    badge: null,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <motion.div
      initial={false}
      animate={{
        width: isCollapsed ? 80 : 240,
      }}
      transition={{
        duration: 300,
        ease: "easeInOut",
      }}
      className="hidden md:flex md:flex-col h-screen border-r bg-card sticky top-0"
    >
      {/* Sidebar Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b">
        <div className={cn("flex items-center gap-2", isCollapsed && "justify-center")}>
          {!isCollapsed && (
            <>
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">RX</span>
              </div>
              <span className="font-bold text-lg">LPG RouteX</span>
            </>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">RX</span>
            </div>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-8 h-8 p-0"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link key={item.name} href={item.href}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {!isCollapsed && (
                  <>
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <Badge
                        variant={isActive ? "secondary" : "default"}
                        className={cn(
                          "text-xs",
                          isActive
                            ? "bg-primary-foreground text-primary"
                            : item.badge === "Live"
                            ? "bg-green-500 text-white animate-pulse"
                            : ""
                        )}
                      >
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
                {isCollapsed && item.badge === "Live" && (
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* Bottom Section */}
      <div className="border-t p-4">
        {!isCollapsed && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>System Status</span>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Active Vehicles</span>
                <span className="font-medium">8/10</span>
              </div>
              <div className="flex justify-between">
                <span>On-time Rate</span>
                <span className="font-medium text-lime-600">94%</span>
              </div>
              <div className="flex justify-between">
                <span>Fuel Efficiency</span>
                <span className="font-medium text-lime-600">Good</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}