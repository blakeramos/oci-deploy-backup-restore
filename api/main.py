#!/usr/bin/env python3
"""
main.py - FastAPI Backend for OCI DataProtect MVP Dashboard

Enterprise-grade REST API for backup operations, policy management,
and compliance reporting. Demonstrates API-first architecture.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Optional, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import (
    BackupRequest, BackupResponse, BackupStatus,
    RestoreRequest, RestoreResponse,
    PolicyResponse, PolicyCreateRequest,
    ValidationReport, DashboardMetrics,
    HealthCheck
)
from api.services.backup_service import BackupService
from api.services.policy_service import PolicyService
from api.services.validation_service import ValidationService
from api.services.metrics_service import MetricsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
backup_service: Optional[BackupService] = None
policy_service: Optional[PolicyService] = None
validation_service: Optional[ValidationService] = None
metrics_service: Optional[MetricsService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI application"""
    global backup_service, policy_service, validation_service, metrics_service
    
    # Startup
    logger.info("Initializing OCI DataProtect API...")
    backup_service = BackupService()
    policy_service = PolicyService()
    validation_service = ValidationService()
    metrics_service = MetricsService()
    logger.info("API initialization complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    # Cleanup resources if needed


# Create FastAPI application
app = FastAPI(
    title="OCI DataProtect MVP API",
    description="Enterprise-grade backup and recovery API for Oracle Cloud Infrastructure",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns API status and service availability.
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services={
            "backup": "operational",
            "policy": "operational",
            "validation": "operational",
            "metrics": "operational"
        }
    )


@app.get("/api/version", tags=["Health"])
async def get_version():
    """Get API version and build information"""
    return {
        "version": "1.0.0",
        "api_name": "OCI DataProtect MVP",
        "build_date": "2025-01-06",
        "features": [
            "Instance Principals Authentication",
            "Auto-tuned Storage",
            "Immutable Backups",
            "Hardware-backed Encryption",
            "Policy Automation",
            "Backup Validation"
        ]
    }


# ============================================================================
# Dashboard Metrics Endpoints
# ============================================================================

@app.get("/api/v1/dashboard/metrics", response_model=DashboardMetrics, tags=["Dashboard"])
async def get_dashboard_metrics(compartment_id: str):
    """
    Get real-time dashboard metrics for a compartment.
    
    Returns:
    - Active jobs count
    - Success rate (30 days)
    - Storage usage
    - Cost savings
    - SLA compliance metrics
    """
    try:
        metrics = await metrics_service.get_dashboard_metrics(compartment_id)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/recent-jobs", tags=["Dashboard"])
async def get_recent_jobs(compartment_id: str, limit: int = 10):
    """Get recent backup jobs with status"""
    try:
        jobs = await metrics_service.get_recent_jobs(compartment_id, limit)
        return {"jobs": jobs}
    except Exception as e:
        logger.error(f"Failed to get recent jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/dashboard/storage-trends", tags=["Dashboard"])
async def get_storage_trends(compartment_id: str, days: int = 7):
    """Get storage usage trends over time"""
    try:
        trends = await metrics_service.get_storage_trends(compartment_id, days)
        return {"trends": trends}
    except Exception as e:
        logger.error(f"Failed to get storage trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Backup Operations Endpoints
# ============================================================================

@app.post("/api/v1/backup/start", response_model=BackupResponse, tags=["Backup"])
async def start_backup(
    request: BackupRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a backup job for a VM instance.
    
    Creates backups for boot volume and all attached block volumes.
    Optionally validates the backup after completion.
    """
    try:
        logger.info(f"Starting backup for instance: {request.instance_id}")
        
        # Start backup job
        job_id = await backup_service.start_backup(
            compartment_id=request.compartment_id,
            instance_id=request.instance_id,
            policy_id=request.policy_id,
            validate=request.validate_after_backup
        )
        
        # Add validation task if requested
        if request.validate_after_backup:
            background_tasks.add_task(
                backup_service.validate_backup_async,
                job_id
            )
        
        return BackupResponse(
            job_id=job_id,
            status=BackupStatus.RUNNING,
            message="Backup job started successfully",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backup/status/{job_id}", response_model=BackupResponse, tags=["Backup"])
async def get_backup_status(job_id: str):
    """Get status of a backup job"""
    try:
        status = await backup_service.get_job_status(job_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    except Exception as e:
        logger.error(f"Failed to get backup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backup/list", tags=["Backup"])
async def list_backups(
    compartment_id: str,
    limit: int = 100,
    backup_type: Optional[str] = None
):
    """
    List all backups in a compartment.
    
    Optionally filter by backup type (boot_volume, block_volume).
    """
    try:
        backups = await backup_service.list_backups(
            compartment_id=compartment_id,
            limit=limit,
            backup_type=backup_type
        )
        return {"backups": backups, "count": len(backups)}
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/backup/{backup_id}", tags=["Backup"])
async def delete_backup(backup_id: str):
    """
    Delete a backup (if not immutable).
    
    Note: Immutable backups cannot be deleted until retention period expires.
    """
    try:
        result = await backup_service.delete_backup(backup_id)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Restore Operations Endpoints
# ============================================================================

@app.post("/api/v1/restore/start", response_model=RestoreResponse, tags=["Restore"])
async def start_restore(request: RestoreRequest):
    """
    Start a restore job to create a new VM from backups.
    
    Restores boot volume and optionally block volumes to a new instance.
    """
    try:
        logger.info(f"Starting restore from backup: {request.boot_backup_id}")
        
        job_id = await backup_service.start_restore(
            compartment_id=request.compartment_id,
            availability_domain=request.availability_domain,
            subnet_id=request.subnet_id,
            shape=request.shape,
            boot_backup_id=request.boot_backup_id,
            block_backup_ids=request.block_backup_ids or []
        )
        
        return RestoreResponse(
            job_id=job_id,
            status="running",
            message="Restore job started successfully",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/restore/status/{job_id}", tags=["Restore"])
async def get_restore_status(job_id: str):
    """Get status of a restore job"""
    try:
        status = await backup_service.get_restore_status(job_id)
        return status
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    except Exception as e:
        logger.error(f"Failed to get restore status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Policy Management Endpoints
# ============================================================================

@app.get("/api/v1/policies", response_model=List[PolicyResponse], tags=["Policies"])
async def list_policies(enabled_only: bool = False):
    """
    List all backup policies.
    
    Optionally filter to show only enabled policies.
    """
    try:
        policies = await policy_service.list_policies(enabled_only=enabled_only)
        return policies
    except Exception as e:
        logger.error(f"Failed to list policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/policies/{policy_id}", response_model=PolicyResponse, tags=["Policies"])
async def get_policy(policy_id: str):
    """Get details of a specific policy"""
    try:
        policy = await policy_service.get_policy(policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/policies", response_model=PolicyResponse, tags=["Policies"])
async def create_policy(request: PolicyCreateRequest):
    """
    Create a new backup policy.
    
    Defines schedule, retention, and target resources for automated backups.
    """
    try:
        policy = await policy_service.create_policy(request)
        return policy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/policies/{policy_id}", response_model=PolicyResponse, tags=["Policies"])
async def update_policy(policy_id: str, updates: Dict):
    """Update an existing policy"""
    try:
        policy = await policy_service.update_policy(policy_id, updates)
        return policy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/policies/{policy_id}", tags=["Policies"])
async def delete_policy(policy_id: str):
    """Delete a backup policy"""
    try:
        await policy_service.delete_policy(policy_id)
        return {"message": f"Policy {policy_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/policies/{policy_id}/enforce", tags=["Policies"])
async def enforce_policy(policy_id: str, compartment_id: str):
    """
    Enforce retention policy by cleaning up old backups.
    
    Deletes backups older than the policy's retention period.
    """
    try:
        result = await policy_service.enforce_policy(policy_id, compartment_id)
        return result
    except Exception as e:
        logger.error(f"Failed to enforce policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Validation & Compliance Endpoints
# ============================================================================

@app.post("/api/v1/validation/backup/{backup_id}", tags=["Validation"])
async def validate_backup(backup_id: str, backup_type: str):
    """
    Validate a specific backup.
    
    Checks backup existence, metadata, encryption, and integrity.
    """
    try:
        result = await validation_service.validate_backup(backup_id, backup_type)
        return result
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/validation/compartment/{compartment_id}", 
         response_model=ValidationReport, 
         tags=["Validation"])
async def validate_compartment(
    compartment_id: str,
    background_tasks: BackgroundTasks
):
    """
    Validate all backups in a compartment.
    
    Generates a comprehensive compliance report.
    This operation runs in the background for large compartments.
    """
    try:
        # Start validation in background
        job_id = await validation_service.start_compartment_validation(
            compartment_id
        )
        
        return {
            "job_id": job_id,
            "status": "running",
            "message": "Validation started. Use GET /api/v1/validation/report/{job_id} to check status"
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/validation/report/{job_id}", tags=["Validation"])
async def get_validation_report(job_id: str):
    """Get validation report for a completed validation job"""
    try:
        report = await validation_service.get_report(job_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get validation report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cost Analytics Endpoints
# ============================================================================

@app.get("/api/v1/cost/analysis", tags=["Cost"])
async def get_cost_analysis(compartment_id: str, days: int = 30):
    """
    Get cost analysis for backup operations.
    
    Returns:
    - Current spending
    - Cost trends
    - Savings from lifecycle policies
    - Comparison vs traditional solutions
    """
    try:
        analysis = await metrics_service.get_cost_analysis(compartment_id, days)
        return analysis
    except Exception as e:
        logger.error(f"Failed to get cost analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cost/savings", tags=["Cost"])
async def get_cost_savings(compartment_id: str):
    """
    Calculate cost savings vs traditional backup solutions.
    
    Compares OCI native approach vs Cohesity, Veeam, etc.
    """
    try:
        savings = await metrics_service.calculate_savings(compartment_id)
        return savings
    except Exception as e:
        logger.error(f"Failed to calculate savings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
