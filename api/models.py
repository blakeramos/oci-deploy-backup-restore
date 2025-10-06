"""
models.py - Pydantic models for request/response validation

Defines all data models used by the FastAPI application.
Ensures type safety and automatic API documentation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


# ============================================================================
# Enums
# ============================================================================

class BackupStatus(str, Enum):
    """Backup job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATING = "validating"


class BackupFrequency(str, Enum):
    """Backup schedule frequency"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RetentionClass(str, Enum):
    """Retention classification"""
    STANDARD = "standard"
    EXTENDED = "extended"
    LONG_TERM = "long_term"
    PERMANENT = "permanent"


# ============================================================================
# Health Check Models
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(..., description="Individual service statuses")


# ============================================================================
# Backup Models
# ============================================================================

class BackupRequest(BaseModel):
    """Request to start a backup job"""
    compartment_id: str = Field(..., description="OCI compartment OCID")
    instance_id: str = Field(..., description="Instance OCID to backup")
    policy_id: Optional[str] = Field(None, description="Backup policy to apply")
    validate_after_backup: bool = Field(
        default=True,
        description="Automatically validate backup after completion"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "compartment_id": "ocid1.compartment.oc1..aaa",
                "instance_id": "ocid1.instance.oc1..aaa",
                "policy_id": "prod-daily",
                "validate_after_backup": True
            }
        }


class BackupResponse(BaseModel):
    """Response from backup operation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: BackupStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    details: Optional[Dict] = Field(None, description="Additional details")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "backup-job-12345",
                "status": "running",
                "message": "Backup job started successfully",
                "timestamp": "2025-01-06T10:00:00Z",
                "details": {
                    "boot_backup_id": "ocid1.bootbackup.oc1..aaa",
                    "volume_backup_ids": ["ocid1.volumebackup.oc1..aaa"]
                }
            }
        }


# ============================================================================
# Restore Models
# ============================================================================

class RestoreRequest(BaseModel):
    """Request to start a restore job"""
    compartment_id: str = Field(..., description="Target compartment")
    availability_domain: str = Field(..., description="Target availability domain")
    subnet_id: str = Field(..., description="Target subnet")
    shape: str = Field(..., description="Instance shape", example="VM.Standard.E5.Flex")
    boot_backup_id: str = Field(..., description="Boot volume backup OCID")
    block_backup_ids: Optional[List[str]] = Field(
        default=[],
        description="Block volume backup OCIDs"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "compartment_id": "ocid1.compartment.oc1..aaa",
                "availability_domain": "oDQa:US-ASHBURN-AD-1",
                "subnet_id": "ocid1.subnet.oc1..aaa",
                "shape": "VM.Standard.E5.Flex",
                "boot_backup_id": "ocid1.bootbackup.oc1..aaa",
                "block_backup_ids": ["ocid1.volumebackup.oc1..aaa"]
            }
        }


class RestoreResponse(BaseModel):
    """Response from restore operation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Response timestamp")
    instance_id: Optional[str] = Field(None, description="Restored instance OCID")


# ============================================================================
# Policy Models
# ============================================================================

class PolicyCreateRequest(BaseModel):
    """Request to create a backup policy"""
    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    frequency: BackupFrequency = Field(..., description="Backup frequency")
    retention_days: int = Field(..., ge=1, description="Retention period in days")
    retention_class: RetentionClass = Field(..., description="Retention classification")
    schedule: str = Field(default="0 2 * * *", description="Cron expression")
    enabled: bool = Field(default=True, description="Policy enabled state")
    validate_backups: bool = Field(default=True, description="Validate after backup")
    encrypt_backups: bool = Field(default=True, description="Encrypt backups")
    immutable_backups: bool = Field(default=False, description="Use immutable storage")
    target_compartments: List[str] = Field(default=[], description="Target compartments")
    target_tags: Dict[str, str] = Field(default={}, description="Resource tags to match")
    
    class Config:
        schema_extra = {
            "example": {
                "policy_id": "prod-daily",
                "name": "Production Daily Backup",
                "description": "Daily backups for production workloads",
                "frequency": "daily",
                "retention_days": 90,
                "retention_class": "extended",
                "schedule": "0 2 * * *",
                "enabled": True,
                "validate_backups": True,
                "encrypt_backups": True,
                "immutable_backups": True,
                "target_compartments": [],
                "target_tags": {"Environment": "Production"}
            }
        }


class PolicyResponse(BaseModel):
    """Response with policy details"""
    policy_id: str
    name: str
    description: str
    frequency: str
    retention_days: int
    retention_class: str
    schedule: str
    enabled: bool
    validate_backups: bool
    encrypt_backups: bool
    immutable_backups: bool
    target_compartments: List[str]
    target_tags: Dict[str, str]
    created_at: str
    updated_at: str


# ============================================================================
# Validation Models
# ============================================================================

class ValidationReport(BaseModel):
    """Validation report for backups"""
    report_id: str = Field(..., description="Report identifier")
    compartment_id: str = Field(..., description="Compartment OCID")
    report_date: str = Field(..., description="Report generation timestamp")
    summary: Dict = Field(..., description="Summary statistics")
    status: str = Field(..., description="Overall compliance status")
    failed_backups: List[str] = Field(default=[], description="Failed backup OCIDs")
    recommendations: List[str] = Field(default=[], description="Recommendations")
    details: Optional[List[Dict]] = Field(None, description="Detailed results")
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "validation-12345",
                "compartment_id": "ocid1.compartment.oc1..aaa",
                "report_date": "2025-01-06T10:00:00Z",
                "summary": {
                    "total_backups": 50,
                    "passed": 48,
                    "failed": 1,
                    "warnings": 1,
                    "compliance_rate": "96.0%"
                },
                "status": "COMPLIANT",
                "failed_backups": ["ocid1.volumebackup.oc1..failed"],
                "recommendations": [
                    "Enable encryption for 2 unencrypted backups",
                    "Investigate failed backup"
                ]
            }
        }


# ============================================================================
# Dashboard Models
# ============================================================================

class DashboardMetrics(BaseModel):
    """Real-time dashboard metrics"""
    compartment_id: str = Field(..., description="Compartment OCID")
    timestamp: str = Field(..., description="Metrics timestamp")
    active_jobs: int = Field(..., description="Currently active backup jobs")
    success_rate: float = Field(..., description="30-day success rate percentage")
    total_backups: int = Field(..., description="Total backup count")
    storage_used_gb: float = Field(..., description="Storage used in GB")
    storage_capacity_gb: float = Field(..., description="Total storage capacity in GB")
    monthly_cost: float = Field(..., description="Estimated monthly cost in USD")
    cost_savings: float = Field(..., description="Monthly savings vs traditional solutions")
    sla_compliance: Dict = Field(..., description="SLA compliance metrics")
    
    class Config:
        schema_extra = {
            "example": {
                "compartment_id": "ocid1.compartment.oc1..aaa",
                "timestamp": "2025-01-06T10:00:00Z",
                "active_jobs": 3,
                "success_rate": 99.9,
                "total_backups": 150,
                "storage_used_gb": 45000,
                "storage_capacity_gb": 100000,
                "monthly_cost": 3200,
                "cost_savings": 5300,
                "sla_compliance": {
                    "rto_hours": 0.5,
                    "rto_target": 2.0,
                    "rpo_minutes": 15,
                    "rpo_target": 60,
                    "availability_percent": 99.99
                }
            }
        }


class JobInfo(BaseModel):
    """Information about a backup job"""
    job_id: str = Field(..., description="Job identifier")
    instance_id: str = Field(..., description="Instance OCID")
    instance_name: str = Field(..., description="Instance name")
    status: BackupStatus = Field(..., description="Job status")
    start_time: str = Field(..., description="Job start time")
    end_time: Optional[str] = Field(None, description="Job end time")
    duration_seconds: Optional[int] = Field(None, description="Job duration in seconds")
    progress_percent: int = Field(..., description="Progress percentage")


class StorageTrend(BaseModel):
    """Storage usage trend data point"""
    date: str = Field(..., description="Date")
    storage_gb: float = Field(..., description="Storage used in GB")
    backup_count: int = Field(..., description="Number of backups")
    cost: float = Field(..., description="Daily cost")


# ============================================================================
# Cost Models
# ============================================================================

class CostAnalysis(BaseModel):
    """Cost analysis for backup operations"""
    compartment_id: str
    period_days: int
    current_monthly_cost: float = Field(..., description="Current monthly cost in USD")
    projected_annual_cost: float = Field(..., description="Projected annual cost")
    cost_breakdown: Dict[str, float] = Field(..., description="Cost breakdown by service")
    trends: List[Dict] = Field(..., description="Cost trends over time")
    optimization_opportunities: List[str] = Field(
        default=[],
        description="Cost optimization recommendations"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "compartment_id": "ocid1.compartment.oc1..aaa",
                "period_days": 30,
                "current_monthly_cost": 3200.00,
                "projected_annual_cost": 38400.00,
                "cost_breakdown": {
                    "storage": 2400.00,
                    "compute": 600.00,
                    "networking": 100.00,
                    "other": 100.00
                },
                "trends": [],
                "optimization_opportunities": [
                    "Enable lifecycle policies for 20% storage savings",
                    "Use archive storage for old backups"
                ]
            }
        }


class CostSavings(BaseModel):
    """Cost savings comparison"""
    oci_monthly_cost: float = Field(..., description="OCI native solution cost")
    traditional_monthly_cost: float = Field(..., description="Traditional solution cost")
    monthly_savings: float = Field(..., description="Monthly savings")
    annual_savings: float = Field(..., description="Annual savings")
    savings_percentage: float = Field(..., description="Savings percentage")
    comparison: Dict[str, float] = Field(..., description="Comparison with vendors")
    
    class Config:
        schema_extra = {
            "example": {
                "oci_monthly_cost": 3200.00,
                "traditional_monthly_cost": 8500.00,
                "monthly_savings": 5300.00,
                "annual_savings": 63600.00,
                "savings_percentage": 62.4,
                "comparison": {
                    "Cohesity": 8500.00,
                    "Veeam": 6200.00,
                    "Commvault": 9200.00
                }
            }
        }
