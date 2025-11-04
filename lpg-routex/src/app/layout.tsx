import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from '@/components/providers'
import { Navbar } from '@/components/layout/navbar'
import { Sidebar } from '@/components/layout/sidebar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'LPG RouteX',
    template: '%s | LPG RouteX'
  },
  description: 'Modern LPG delivery route optimization platform for efficient logistics management',
  keywords: ['LPG', 'delivery', 'route optimization', 'logistics', 'fuel efficiency'],
  authors: [{ name: 'Subhajit Roy' }],
  creator: 'Subhajit Roy',
  publisher: 'LPG RouteX',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    }
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#007AFF" />
      </head>
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <div className="flex">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Navbar />
              <main className="flex-1 overflow-auto">
                <Providers>
                  {children}
                </Providers>
              </main>
            </div>
          </div>
        </div>
      </body>
    </html>
  )
}