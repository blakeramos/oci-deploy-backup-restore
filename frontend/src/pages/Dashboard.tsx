import React, { useState, useEffect } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
} from '@mui/material'
import {
  CheckCircle,
  Error,
  Storage,
  AttachMoney,
  Speed,
  Security,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { apiClient } from '../services/api'

const COLORS = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [recentJobs, setRecentJobs] = useState<any[]>([])
  const [storageTrends, setStorageTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const compartmentId = 'demo-compartment'
      
      const [metricsRes, jobsRes, trendsRes] = await Promise.all([
        apiClient.get(`/dashboard/metrics?compartment_id=${compartmentId}`),
        apiClient.get(`/dashboard/recent-jobs?compartment_id=${compartmentId}&limit=5`),
        apiClient.get(`/dashboard/storage-trends?compartment_id=${compartmentId}&days=7`),
      ])

      setMetrics(metricsRes.data)
      setRecentJobs(jobsRes.data.jobs)
      setStorageTrends(trendsRes.data.trends)
      setLoading(false)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading dashboard metrics...
        </Typography>
      </Box>
    )
  }

  const successRate = metrics?.success_rate || 0
  const storageUsed = metrics?.storage_used_gb || 0
  const storageCapacity = metrics?.storage_capacity_gb || 100000
  const storagePercent = (storageUsed / storageCapacity) * 100

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Dashboard Overview
      </Typography>

      {/* Top Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Active Jobs */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    Active Jobs
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {metrics?.active_jobs || 0}
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Success Rate */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    Success Rate (30d)
                  </Typography>
                  <Typography variant="h3" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {successRate.toFixed(1)}%
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Storage Used */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    Storage Used
                  </Typography>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 'bold' }}>
                    {(storageUsed / 1000).toFixed(1)} TB
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    {storagePercent.toFixed(1)}% of capacity
                  </Typography>
                </Box>
                <Storage sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Monthly Savings */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    Monthly Savings
                  </Typography>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 'bold' }}>
                    ${(metrics?.cost_savings || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    vs traditional solutions
                  </Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 48, color: 'rgba(255,255,255,0.3)' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Backup Jobs */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Backup Jobs
            </Typography>
            <Box>
              {recentJobs.map((job: any) => (
                <Box
                  key={job.job_id}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 2,
                    borderBottom: '1px solid #eee',
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body1" fontWeight="bold">
                      {job.instance_name}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Started: {new Date(job.start_time).toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    {job.status === 'completed' && (
                      <Chip
                        label="Completed"
                        color="success"
                        size="small"
                        icon={<CheckCircle />}
                      />
                    )}
                    {job.status === 'running' && (
                      <Box>
                        <Chip label="Running" color="primary" size="small" />
                        <LinearProgress
                          variant="determinate"
                          value={job.progress_percent}
                          sx={{ mt: 1, width: 100 }}
                        />
                      </Box>
                    )}
                    {job.status === 'failed' && (
                      <Chip label="Failed" color="error" size="small" icon={<Error />} />
                    )}
                  </Box>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* SLA Compliance */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              SLA Compliance
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    RTO (Recovery Time Objective)
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ✓ {metrics?.sla_compliance?.rto_hours || 0.5}h / {metrics?.sla_compliance?.rto_target || 2}h target
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={75}
                  color="success"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    RPO (Recovery Point Objective)
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ✓ {metrics?.sla_compliance?.rpo_minutes || 15}min / {metrics?.sla_compliance?.rpo_target || 60}min target
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={75}
                  color="success"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    Availability
                  </Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ✓ {metrics?.sla_compliance?.availability_percent || 99.99}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={99.99}
                  color="success"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Storage Trends Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Storage Usage Trends (7 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={storageTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Storage (GB)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="storage_gb"
                  stroke="#F80000"
                  fill="#F80000"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Key Features Highlight */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'white', mb: 2 }}>
              ✨ OCI Native Advantages Demonstrated
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', color: 'white' }}>
                  <Security sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body2" fontWeight="bold">
                    Instance Principals
                  </Typography>
                  <Typography variant="caption">
                    Zero-key authentication
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', color: 'white' }}>
                  <Storage sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body2" fontWeight="bold">
                    Auto-Tuned Storage
                  </Typography>
                  <Typography variant="caption">
                    Automatic IOPS scaling
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', color: 'white' }}>
                  <CheckCircle sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body2" fontWeight="bold">
                    Immutable Backups
                  </Typography>
                  <Typography variant="caption">
                    90-day retention locks
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', color: 'white' }}>
                  <AttachMoney sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body2" fontWeight="bold">
                    Cost Optimization
                  </Typography>
                  <Typography variant="caption">
                    70% lifecycle savings
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
