"""
metrics_service.py - Metrics and analytics service

Business logic for dashboard metrics, cost analysis, and trends.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import random

logger = logging.getLogger(__name__)


class MetricsService:
    """Service for metrics and analytics"""
    
    def __init__(self):
        logger.info("MetricsService initialized")
    
    async def get_dashboard_metrics(self, compartment_id: str) -> Dict:
        """Get real-time dashboard metrics"""
        # Mock data for MVP demo - showcases OCI advantages
        return {
            "compartment_id": compartment_id,
            "timestamp": datetime.utcnow().isoformat(),
            "active_jobs": 3,
            "success_rate": 99.9,
            "total_backups": 150,
            "storage_used_gb": 45000,
            "storage_capacity_gb": 100000,
            "monthly_cost": 3200.00,
            "cost_savings": 5300.00,
            "sla_compliance": {
                "rto_hours": 0.5,
                "rto_target": 2.0,
                "rpo_minutes": 15,
                "rpo_target": 60,
                "availability_percent": 99.99
            }
        }
    
    async def get_recent_jobs(self, compartment_id: str, limit: int = 10) -> List[Dict]:
        """Get recent backup jobs"""
        # Mock data for demo
        jobs = [
            {
                "job_id": "backup-abc123",
                "instance_id": "ocid1.instance.oc1..prod-web-01",
                "instance_name": "prod-web-01",
                "status": "completed",
                "start_time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "duration_seconds": 120,
                "progress_percent": 100
            },
            {
                "job_id": "backup-def456",
                "instance_id": "ocid1.instance.oc1..prod-db-01",
                "instance_name": "prod-db-01",
                "status": "running",
                "start_time": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                "end_time": None,
                "duration_seconds": None,
                "progress_percent": 45
            },
            {
                "job_id": "backup-ghi789",
                "instance_id": "ocid1.instance.oc1..prod-app-01",
                "instance_name": "prod-app-01",
                "status": "completed",
                "start_time": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "end_time": (datetime.utcnow() - timedelta(minutes=13)).isoformat(),
                "duration_seconds": 120,
                "progress_percent": 100
            }
        ]
        return jobs[:limit]
    
    async def get_storage_trends(self, compartment_id: str, days: int = 7) -> List[Dict]:
        """Get storage usage trends"""
        # Mock trend data
        trends = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "storage_gb": 40000 + (i * 500) + random.randint(-100, 100),
                "backup_count": 145 + i,
                "cost": 2800 + (i * 40)
            })
        return trends
    
    async def get_cost_analysis(self, compartment_id: str, days: int = 30) -> Dict:
        """Get cost analysis"""
        return {
            "compartment_id": compartment_id,
            "period_days": days,
            "current_monthly_cost": 3200.00,
            "projected_annual_cost": 38400.00,
            "cost_breakdown": {
                "storage": 2400.00,
                "compute": 600.00,
                "networking": 100.00,
                "other": 100.00
            },
            "trends": [
                {"date": "2024-12-06", "cost": 105.5},
                {"date": "2025-01-06", "cost": 107.2}
            ],
            "optimization_opportunities": [
                "Enable lifecycle policies for 20% storage savings",
                "Use archive storage for backups older than 90 days",
                "Reduce retention period for dev/test backups"
            ]
        }
    
    async def calculate_savings(self, compartment_id: str) -> Dict:
        """Calculate cost savings vs traditional solutions"""
        return {
            "oci_monthly_cost": 3200.00,
            "traditional_monthly_cost": 8500.00,
            "monthly_savings": 5300.00,
            "annual_savings": 63600.00,
            "savings_percentage": 62.4,
            "comparison": {
                "Cohesity": 8500.00,
                "Veeam": 6200.00,
                "Commvault": 9200.00,
                "Rubrik": 7800.00
            },
            "value_props": [
                "60% lower TCO than traditional solutions",
                "Zero licensing fees - OCI native services only",
                "70% storage cost reduction through lifecycle policies",
                "No hidden egress charges",
                "Predictable, transparent pricing"
            ]
        }
