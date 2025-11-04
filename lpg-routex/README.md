# LPG RouteX

A modern, responsive web application for optimizing LPG (Liquefied Petroleum Gas) delivery routes. The platform helps logistics managers plan, monitor, and adjust delivery operations efficiently with a focus on clarity, usability, and real-time visibility.

## 🚀 Features

### 🗺️ Core Functionality
- **Real-time Dashboard**: Today's overview with live metrics, system health, and fleet status
- **Route Planner**: Intelligent route optimization with multiple algorithms (shortest distance, minimum fuel cost)
- **Live Tracking**: Real-time GPS tracking with interactive maps and route visualization
- **Analytics**: Comprehensive analytics with charts and performance metrics
- **Admin Panel**: User management, system configuration, and activity logs

### 📊 Key Metrics
- Total Deliveries: Track daily delivery volume and trends
- Active Vehicles: Monitor fleet status and utilization
- Route Efficiency: Calculate optimization improvements
- Fuel Cost: Monitor fuel consumption and cost savings
- System Performance: API response times and uptime

### 🎯 User Experience
- **Modern Design**: Clean, intuitive interface with Tailwind CSS
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Updates**: Live data streaming via WebSockets
- **Dark Mode**: Eye-friendly dark theme toggle
- **Interactive Maps**: Zoom, pan, and route visualization

## 🏗️ Architecture

### Frontend Technology Stack
- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: TanStack Query for server state
- **Animations**: Framer Motion for smooth transitions
- **Maps**: Mapbox GL JS for interactive mapping
- **Charts**: Recharts for data visualization

### Backend Technology Stack
- **Database**: PostgreSQL + PostGIS for spatial data
- **API**: RESTful API with Next.js API routes
- **Real-time**: WebSockets for live updates
- **File Handling**: Multer for secure file uploads
- **Authentication**: JWT-based auth with RBAC

### 🗺️ Security & Compliance
- **Authentication**: Role-based access control
- **Data Privacy**: Secure handling of sensitive delivery data
- **Audit Trail**: Comprehensive activity logging
- **Input Validation**: Input sanitization and validation
- **CORS**: Secure cross-origin requests
- **Rate Limiting**: API rate limiting
- **Security Headers**: Content Security Policy

## 🚀 Quick Start

### Prerequisites
- Node.js 20.0+
- npm 10.0+
- PostgreSQL database
- Mapbox access token (optional, falls back to OpenStreetMap)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sr857/DeliveryLpg.git
   cd DeliveryLpg/lpg-routex
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env.local
   # Configure your database and Mapbox token
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open the application**
   Navigate to `http://localhost:3000`

## 📱� Pages Overview

### Dashboard (`/`)
- Today's overview with real-time metrics
- Interactive route map showing current deliveries
- Fleet status and performance indicators
- Recent deliveries table with status tracking

### Route Planner (`/planner`)
- CSV upload or manual delivery point input
- Multiple optimization modes (shortest distance, minimum fuel cost)
- Vehicle capacity and time window configuration
- Interactive route visualization with stop details

### Live Tracking (`/tracking`)
- Full-width interactive map with real-time vehicle positions
- Vehicle status indicators (Active, Idle, Maintenance, Offline)
- Live telemetry and performance metrics
- Route recalculation for delays

### Analytics (`/analytics`)
- Comprehensive delivery performance charts
- Fuel consumption trends and optimization metrics
- Delivery success rates and delay analysis
- Data export capabilities (PDF, CSV, JSON)
- Date range and region filters

### Admin Panel (`/admin`)
- User management with role-based permissions
- System configuration and settings
- Activity logs and audit trails
- Integration configuration
- Performance monitoring and alerting

## 🎨 Design System

### Color Palette
- **Primary**: #007AFF (Blue) - Main action buttons, highlights
- **Secondary**: #66BB6A (Lime Green) - Success indicators
- **Background**: #F9FAFB (Light Gray) - Page background
- **Foreground**: #111827 (Dark Gray) - Primary text
- **Accent**: #66BB6A (Lime Green) - Active states

### Typography
- **Font**: Inter (Poppins alternative)
- **Headers**: Semi-bold for section titles
- **Body**: Regular for content
- **Small Text**: 12-14px for metadata

### Components
- **Cards**: Rounded corners, soft shadows, hover states
- **Buttons**: Consistent variants (primary, secondary, outline)
- **Badges**: Color-coded status indicators
- **Progress**: Visual progress indicators
- **Tables**: Clean, accessible data tables
- **Navigation**: Collapsible sidebar with route icons

### Responsive Design
- **Mobile**: Collapsible sidebar, full-width content
- **Tablet**: Side navigation with main content
- **Desktop**: Full layout with all panels visible
- **Adaptive**: Responsive grids and flexible containers

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://localhost:5432/lpg_routex
POSTGRES_USER=lpg_routex
POSTGRES_PASSWORD=password
POSTGRES_DB=lpg_routex

# Authentication
JWT_SECRET=your-secret-key-here
JWT_EXPIRY=24h

# Mapbox (Optional)
MAPBOX_ACCESS_TOKEN=your-mapbox-token-here

# Application
NEXTAUTH_SECRET=your-nextauth-secret
NODE_ENV=development
```

### Configuration Files
- **Tailwind CSS**: Custom color scheme and components
- **Next.js**: App Router and middleware configuration
- **TypeScript**: Strict type checking enabled
- **ESLint**: Comprehensive linting rules

## 🚀 API Integration

### Core Endpoints
- `/api/auth/*` - Authentication endpoints
- `/api/deliveries/*` - Delivery management
- `/api/vehicles/*` - Vehicle tracking
- `/api/routes/*` - Route optimization
- `/api/analytics/*` - Analytics data
- `/api/admin/*` - Admin operations

### WebSocket Events
- `analysis:progress` - Route optimization progress
- `vehicle:location` - Real-time GPS updates
- `delivery:status` - Delivery status changes
- `system:health` - System health metrics
- `alert:*` - System alerts

## 📊 Data Models

### Core Entities
- **Vehicle**: Truck information and status
- **Route**: Delivery routes and optimization data
- **Delivery**: Individual delivery points and status
- **Driver**: Driver information and contact details
- **Analytics**: Performance metrics and KPIs
- **User**: User accounts and permissions
- **Audit**: System activity logs

### Database Schema
- PostgreSQL with PostGIS for spatial data
- Normalized structure with proper indexing
- Audit trail for compliance
- Foreign key relationships maintained

## 🔒 Development

### Scripts
```bash
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # Code linting
npm run type-check     # Type checking
npm run db:migrate    # Database migrations
npm run db:studio     # Database studio
```

### Testing
```bash
npm test               # Run all tests
npm run test:watch    # Watch mode testing
npm run test:coverage  # Coverage report
```

## 🚀 Deployment

### Production Build
```bash
npm run build
npm start
```

### Docker Deployment
```bash
docker build -t lpg-routex .
docker run -p 3000:3000 lpg-routex
```

### Cloud Platforms
- **Vercel**: Recommended for Next.js applications
- **AWS**: S3 + RDS + CloudFront
- **Digital Ocean**: App Platform with PostgreSQL
- **Heroku**: Easy deployment for small-medium apps
- **Azure**: Azure App Service with PostgreSQL

## 📊 Monitoring

### Application Metrics
- **Performance**: Page load times, API response times
- **Uptime**: System availability monitoring
- **Error Rates**: 4xx, 5xx error tracking
- **User Analytics**: Usage patterns and features

### System Monitoring
- **Database**: Query performance and connection health
- **API**: Request volume and response times
- **Maps**: Map service integration status
- **WebSocket**: Connection health and message delivery
- **Resource Usage**: CPU, memory, disk I/O

## 🛡️ Security Features

### Authentication
- **JWT-based**: Secure token authentication
- **Role-Based**: Different access levels (Admin, Dispatcher, Viewer)
- **MFA Support**: Multi-factor authentication for admins
- **Session Management**: Secure session handling
- **Password Policy**: Strong password requirements

### Data Protection
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection**: Parameterized queries
- **XSS Protection**: Complete CSP headers
- **Rate Limiting**: API request throttling
- **Audit Trail**: Immutable activity logging

### Access Control
- **RBAC**: Role-based access control
- **Permission Granularity**: Fine-grained permissions
- **Resource Access**: Secure resource-level access
- **API Authorization**: Endpoint protection
- **Data Privacy**: GDPR-like data handling

## 🌐 Integration Capabilities

### Third-Party Services
- **S3/Cloud Storage**: File storage for reports and data
- **Email Services**: Notification systems (SendGrid, AWS SES)
- **SMS Services**: Delivery notifications
- **Payment Gateways**: Payment processing integration
- **Webhooks**: Real-time event notifications

### API Integrations
- **ERP Systems**: Enterprise resource planning
- **GPS Services: Real-time vehicle tracking
- **Map Services**: Route calculation
- **Communication**: Driver messaging platforms
- **Analytics**: Business intelligence platforms
- **Telemetry**: System observability platforms

### Export Options
- **PDF Reports**: Professional report generation
- **Excel/CSV**: Data export for analysis
- **JSON API**: Machine-readable data export
- **XML**: Structured data exchange
- **STIX**: Threat intelligence sharing

## 📋 Support

### Documentation
- **Comprehensive**: Complete feature documentation
- **API Reference**: Full API documentation
- **Deployment Guide**: Production deployment guide
- **Troubleshooting**: Common issues and solutions
- **Architecture Overview**: System design documentation

### Training
- **User Guides**: End-user documentation
- **Admin Training**: Administrative functions
- **Developer Docs**: Technical implementation
- **Video Tutorials**: Video-based training materials

### Contact
- **Email**: support@lpgroutex.com
- **Documentation**: https://docs.lpg-routex.com
- **GitHub**: https://github.com/sr857/DeliveryLpg
- **LinkedIn**: https://linkedin.com/in/sr857

---

**Developed with ❤️ by Subhajit Roy**
**LinkedIn**: linkedin.com/in/sr857

**© 2024 LPG RouteX. All rights reserved.