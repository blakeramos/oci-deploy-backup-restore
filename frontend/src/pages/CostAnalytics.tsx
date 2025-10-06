import React from 'react'
import { Typography, Paper, Box } from '@mui/material'

export default function CostAnalytics() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
        Cost Analytics
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" color="textSecondary">
          Cost analysis and savings comparison dashboard will be displayed here.
        </Typography>
        <Typography variant="body2" sx={{ mt: 2 }}>
          This page will show:
        </Typography>
        <ul>
          <li>Monthly and annual cost breakdown</li>
          <li>Cost savings vs traditional solutions (Cohesity, Veeam)</li>
          <li>Storage lifecycle cost optimization</li>
          <li>Cost trends and projections</li>
        </ul>
      </Paper>
    </Box>
  )
}
