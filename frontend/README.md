# OCI DataProtect MVP - React Frontend

Enterprise-grade dashboard for OCI backup and recovery operations.

## Features

- **Real-time Dashboard** - Live metrics, job status, SLA compliance
- **Interactive Charts** - Storage trends, cost analysis with Recharts
- **Material-UI Design** - Professional, responsive interface
- **Oracle Branding** - Oracle Red theme, enterprise styling
- **API Integration** - Connects to FastAPI backend
- **Auto-refresh** - Updates every 30 seconds

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** - Component library
- **Recharts** - Data visualization
- **Axios** - API client
- **Vite** - Build tool
- **React Router** - Navigation

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:3000

### 3. Start Backend API (in separate terminal)

```bash
cd api
python3 main.py
```

API will run at: http://localhost:8000

## Project Structure

```
frontend/
├── public/                # Static assets
├── src/
│   ├── main.tsx          # App entry point
│   ├── App.tsx           # Main app with navigation
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx      # Main dashboard (implemented)
│   │   ├── BackupJobs.tsx     # Job management
│   │   ├── Policies.tsx       # Policy management
│   │   ├── Validation.tsx     # Compliance reports
│   │   └── CostAnalytics.tsx  # Cost analysis
│   └── services/
│       └── api.ts        # API client
├── package.json
└── vite.config.ts
```

## Creating Missing Pages

To complete the MVP, create stub pages for the remaining routes:

### src/pages/BackupJobs.tsx
```typescript
import React from 'react'
import { Typography, Paper, Box } from '@mui/material'

export default function BackupJobs() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Backup Jobs
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Backup jobs list will be displayed here</Typography>
      </Paper>
    </Box>
  )
}
```

### src/pages/Policies.tsx
```typescript
import React from 'react'
import { Typography, Paper, Box } from '@mui/material'

export default function Policies() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Backup Policies
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Policy management interface</Typography>
      </Paper>
    </Box>
  )
}
```

### src/pages/Validation.tsx
```typescript
import React from 'react'
import { Typography, Paper, Box } from '@mui/material'

export default function Validation() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Backup Validation
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Validation reports and compliance</Typography>
      </Paper>
    </Box>
  )
}
```

### src/pages/CostAnalytics.tsx
```typescript
import React from 'react'
import { Typography, Paper, Box } from '@mui/material'

export default function CostAnalytics() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Cost Analytics
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Cost analysis and savings comparison</Typography>
      </Paper>
    </Box>
  )
}
```

## Dashboard Features

The implemented Dashboard page includes:

### Metrics Cards
- **Active Jobs** - Real-time job count
- **Success Rate** - 30-day success percentage
- **Storage Used** - Current storage with capacity
- **Monthly Savings** - Cost savings vs traditional

### Recent Backup Jobs
- Live job status (completed, running, failed)
- Progress bars for running jobs
- Timestamps and instance names

### SLA Compliance
- RTO (Recovery Time Objective)
- RPO (Recovery Point Objective)
- Availability percentage
- Visual progress indicators

### Storage Trends Chart
- 7-day storage usage graph
- Area chart with Oracle Red branding

### OCI Advantages Highlight
- Instance Principals
- Auto-Tuned Storage
- Immutable Backups
- Cost Optimization

## API Integration

The dashboard connects to these FastAPI endpoints:

```typescript
GET /api/v1/dashboard/metrics?compartment_id=demo
GET /api/v1/dashboard/recent-jobs?compartment_id=demo&limit=5
GET /api/v1/dashboard/storage-trends?compartment_id=demo&days=7
```

## Customization

### Change Oracle Branding Colors

Edit `src/main.tsx`:

```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#F80000', // Oracle Red
    },
    secondary: {
      main: '#312D2A', // Oracle Black
    },
  },
})
```

### Modify Refresh Interval

Edit `src/pages/Dashboard.tsx`:

```typescript
// Change from 30 seconds to desired interval
const interval = setInterval(loadDashboardData, 30000)
```

### Update Compartment ID

Edit the compartmentId in Dashboard.tsx or make it configurable:

```typescript
const compartmentId = 'your-compartment-id'
```

## Building for Production

```bash
npm run build
```

Builds to `dist/` directory. Serve with:

```bash
npm run preview
```

## Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

Access in code:

```typescript
const API_URL = import.meta.env.VITE_API_URL
```

## Troubleshooting

### TypeScript Errors

TypeScript may show errors until dependencies are installed:

```bash
npm install
```

### API Connection Issues

Ensure FastAPI backend is running:

```bash
cd api
python3 main.py
```

Check proxy configuration in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### CORS Issues

FastAPI is configured for CORS with `localhost:3000`. If using different port, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    ...
)
```

## Demo Mode

The dashboard uses mock data from the FastAPI backend's MetricsService. This demonstrates:

- 99.9% success rate
- $5,300/month savings (62%)
- 150 backups under management
- <1 hour RTO, <15 min RPO
- Real-time job tracking

Perfect for OCI DataProtect team demonstrations!

## Next Steps

1. **Install dependencies**: `npm install`
2. **Create stub pages** (copy from examples above)
3. **Start dev server**: `npm run dev`
4. **Start API backend**: `python3 api/main.py`
5. **Open browser**: http://localhost:3000

## Support

For issues or questions about the React frontend, see:
- Main README.md in project root
- FastAPI backend documentation in `api/`
- MVP POC Plan in `MVP_POC_PLAN.md`
