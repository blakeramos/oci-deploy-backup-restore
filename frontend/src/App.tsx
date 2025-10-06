import React from 'react'
import { Routes, Route } from 'react-router-dom'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Backup,
  Policy,
  Assessment,
  AttachMoney,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'

// Import pages
import Dashboard from './pages/Dashboard'
import BackupJobs from './pages/BackupJobs'
import Policies from './pages/Policies'
import Validation from './pages/Validation'
import CostAnalytics from './pages/CostAnalytics'

const drawerWidth = 240

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Backup Jobs', icon: <Backup />, path: '/backups' },
  { text: 'Policies', icon: <Policy />, path: '/policies' },
  { text: 'Validation', icon: <Assessment />, path: '/validation' },
  { text: 'Cost Analytics', icon: <AttachMoney />, path: '/cost' },
]

function App() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Top App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#F80000', // Oracle Red
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
            OCI DataProtect MVP
          </Typography>
          <Typography
            variant="subtitle2"
            sx={{ ml: 2, opacity: 0.9 }}
          >
            Enterprise Backup Management
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <List>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemIcon sx={{ color: location.pathname === item.path ? '#F80000' : 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          backgroundColor: '#F5F5F5',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        <Container maxWidth="xl">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/backups" element={<BackupJobs />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/validation" element={<Validation />} />
            <Route path="/cost" element={<CostAnalytics />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}

export default App
