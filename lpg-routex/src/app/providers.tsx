'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { ReactNode } from 'react'

const queryClient = new QueryClient()

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster
        position="top-right"
        richColors
        toastOptions={{
          style: {
            background: 'hsl(var(--background))',
            border: '1px solid hsl(var(--border))',
            color: 'hsl(var(--foreground))',
            borderRadius: '0.375rem',
            boxShadow:
              '0 10px 25px -2px rgba(0, 0, 0, 0.1)',
          }}
        />
      />
      {children}
    </QueryClientProvider>
  )
}