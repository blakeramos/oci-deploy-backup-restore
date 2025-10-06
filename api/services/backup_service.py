"""
backup_service.py - Backup operations service

Business logic for backup and restore operations.
Integrates with existing backup.py and restore.py scripts.
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict
import sys
import os

# Add python directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'python'))

logger = logging.getLogger(__name__)


class BackupService:
    """Service for backup and restore operations"""
    
    def __init__(self):
        self.jobs = {}  # In-memory job tracking (use database in production)
        logger.info("BackupService initialized")
    
    async def start_backup(
        self,
        compartment_id: str,
        instance_id: str,
        policy_id: Optional[str] = None,
        validate: bool = True
    ) -> str:
        """
        Start a backup job for an instance.
        
        In production, this would:
        1. Call backup.py via subprocess or queue
        2. Track job status in database
        3. Return job ID immediately
        """
        job_id = f"backup-{uuid.uuid4().hex[:12]}"
        
        # Store job info
        self.jobs[job_id] = {
            "job_id": job_id,
            "type": "backup",
            "compartment_id": compartment_id,
            "instance_id": instance_id,
            "policy_id": policy_id,
            "status": "running",
            "start_time": datetime.utcnow().isoformat(),
            "progress": 0
        }
        
        logger.info(f"Started backup job {job_id} for instance {instance_id}")
        
        # TODO: Integrate with python/backup.py
        # subprocess.Popen(['python3', 'backup.py', '--compartment', compartment_id, '--instance', instance_id])
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Dict:
        """Get status of a backup job"""
        if job_id not in self.jobs:
            raise KeyError(f"Job {job_id} not found")
        
        return self.jobs[job_id]
    
    async def list_backups(
        self,
        compartment_id: str,
        limit: int = 100,
        backup_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List backups in a compartment.
        
        TODO: Integrate with OCI SDK to list actual backups
        """
        # Mock data for MVP demo
        return [
            {
                "backup_id": "ocid1.bootbackup.oc1..aaa123",
                "type": "boot_volume",
                "instance_name": "prod-web-01",
                "created": "2025-01-06T08:00:00Z",
                "size_gb": 50,
                "status": "AVAILABLE"
            },
            {
                "backup_id": "ocid1.volumebackup.oc1..aaa456",
                "type": "block_volume",
                "instance_name": "prod-db-01",
                "created": "2025-01-06T02:00:00Z",
                "size_gb": 500,
                "status": "AVAILABLE"
            }
        ]
    
    async def delete_backup(self, backup_id: str) -> Dict:
        """
        Delete a backup if not immutable.
        
        TODO: Integrate with OCI SDK
        """
        logger.info(f"Deleting backup {backup_id}")
        return {"message": f"Backup {backup_id} deleted successfully"}
    
    async def start_restore(
        self,
        compartment_id: str,
        availability_domain: str,
        subnet_id: str,
        shape: str,
        boot_backup_id: str,
        block_backup_ids: List[str]
    ) -> str:
        """
        Start a restore job.
        
        TODO: Integrate with python/restore.py
        """
        job_id = f"restore-{uuid.uuid4().hex[:12]}"
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "type": "restore",
            "compartment_id": compartment_id,
            "boot_backup_id": boot_backup_id,
            "status": "running",
            "start_time": datetime.utcnow().isoformat(),
            "progress": 0
        }
        
        logger.info(f"Started restore job {job_id} from backup {boot_backup_id}")
        
        return job_id
    
    async def get_restore_status(self, job_id: str) -> Dict:
        """Get status of a restore job"""
        if job_id not in self.jobs:
            raise KeyError(f"Job {job_id} not found")
        
        return self.jobs[job_id]
    
    async def validate_backup_async(self, job_id: str):
        """Validate backup after completion (background task)"""
        logger.info(f"Validating backup for job {job_id}")
        # TODO: Call validator.py
        pass
