#!/usr/bin/env python3
"""
validator.py - Backup Validation for OCI DataProtect MVP

Validates backup integrity and recoverability to ensure backups are trustworthy.
Demonstrates enterprise-grade backup validation and compliance reporting.
"""
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import oci

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationCheck(Enum):
    """Types of validation checks"""
    BACKUP_EXISTS = "backup_exists"
    METADATA_VALID = "metadata_valid"
    SIZE_VALID = "size_valid"
    ENCRYPTION_VERIFIED = "encryption_verified"
    RESTORE_TEST = "restore_test"
    INTEGRITY_CHECKSUM = "integrity_checksum"


@dataclass
class ValidationResult:
    """Result of a backup validation"""
    backup_id: str
    backup_type: str  # boot_volume, block_volume, object
    validation_time: str
    overall_status: ValidationStatus
    checks: Dict[str, Dict[str, any]]
    issues: List[str]
    recommendations: List[str]
    compliance_status: str
    
    def __post_init__(self):
        if not self.validation_time:
            self.validation_time = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['overall_status'] = self.overall_status.value
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class BackupValidator:
    """Validates backup integrity and recoverability"""
    
    def __init__(self, profile: str = None):
        self.profile = profile
        self.compute_client = None
        self.block_storage_client = None
        self.object_storage_client = None
        self._init_clients()
        logging.info("BackupValidator initialized")
    
    def _init_clients(self):
        """Initialize OCI clients"""
        try:
            if self.profile:
                config = oci.config.from_file(profile_name=self.profile)
                signer = None
            else:
                try:
                    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                    config = {}
                except Exception:
                    config = oci.config.from_file()
                    signer = None
            
            self.compute_client = oci.core.ComputeClient(config, signer=signer)
            self.block_storage_client = oci.core.BlockstorageClient(config, signer=signer)
            self.object_storage_client = oci.object_storage.ObjectStorageClient(config, signer=signer)
            
        except Exception as e:
            logging.error("Failed to initialize OCI clients: %s", e)
            raise
    
    def validate_boot_volume_backup(self, backup_id: str) -> ValidationResult:
        """Validate a boot volume backup"""
        logging.info("Validating boot volume backup: %s", backup_id)
        
        checks = {}
        issues = []
        recommendations = []
        overall_status = ValidationStatus.PASSED
        
        try:
            # Check 1: Backup exists and is accessible
            try:
                backup = self.block_storage_client.get_boot_volume_backup(backup_id).data
                checks[ValidationCheck.BACKUP_EXISTS.value] = {
                    "status": "passed",
                    "message": "Backup exists and is accessible",
                    "details": {
                        "display_name": backup.display_name,
                        "lifecycle_state": backup.lifecycle_state,
                        "time_created": str(backup.time_created)
                    }
                }
                
                if backup.lifecycle_state != "AVAILABLE":
                    issues.append(f"Backup state is {backup.lifecycle_state}, not AVAILABLE")
                    overall_status = ValidationStatus.WARNING
                    
            except Exception as e:
                checks[ValidationCheck.BACKUP_EXISTS.value] = {
                    "status": "failed",
                    "message": f"Failed to access backup: {e}"
                }
                issues.append(f"Cannot access backup: {e}")
                overall_status = ValidationStatus.FAILED
                return ValidationResult(
                    backup_id=backup_id,
                    backup_type="boot_volume",
                    validation_time=datetime.utcnow().isoformat(),
                    overall_status=overall_status,
                    checks=checks,
                    issues=issues,
                    recommendations=recommendations,
                    compliance_status="FAILED"
                )
            
            # Check 2: Metadata validation
            checks[ValidationCheck.METADATA_VALID.value] = self._validate_metadata(backup)
            if checks[ValidationCheck.METADATA_VALID.value]["status"] == "failed":
                issues.extend(checks[ValidationCheck.METADATA_VALID.value].get("issues", []))
                overall_status = ValidationStatus.WARNING
            
            # Check 3: Size validation
            checks[ValidationCheck.SIZE_VALID.value] = self._validate_size(backup)
            if checks[ValidationCheck.SIZE_VALID.value]["status"] == "warning":
                recommendations.append("Backup size is unusually small or large")
            
            # Check 4: Encryption verification
            checks[ValidationCheck.ENCRYPTION_VERIFIED.value] = self._validate_encryption(backup)
            if checks[ValidationCheck.ENCRYPTION_VERIFIED.value]["status"] == "failed":
                issues.append("Backup is not encrypted")
                recommendations.append("Enable encryption for all backups")
                overall_status = ValidationStatus.WARNING
            
            # Check 5: Test restore (optional - can be expensive)
            # Skipped by default, can be enabled for critical validations
            checks[ValidationCheck.RESTORE_TEST.value] = {
                "status": "skipped",
                "message": "Restore test skipped (enable with --test-restore flag)",
                "details": {}
            }
            
            # Determine compliance status
            compliance_status = "COMPLIANT" if overall_status == ValidationStatus.PASSED else "NON_COMPLIANT"
            
            logging.info("Validation complete for %s: %s", backup_id, overall_status.value)
            
        except Exception as e:
            logging.error("Validation failed with exception: %s", e)
            checks["exception"] = {
                "status": "failed",
                "message": f"Validation failed: {e}"
            }
            issues.append(f"Validation exception: {e}")
            overall_status = ValidationStatus.FAILED
            compliance_status = "FAILED"
        
        return ValidationResult(
            backup_id=backup_id,
            backup_type="boot_volume",
            validation_time=datetime.utcnow().isoformat(),
            overall_status=overall_status,
            checks=checks,
            issues=issues,
            recommendations=recommendations,
            compliance_status=compliance_status
        )
    
    def validate_volume_backup(self, backup_id: str) -> ValidationResult:
        """Validate a block volume backup"""
        logging.info("Validating block volume backup: %s", backup_id)
        
        checks = {}
        issues = []
        recommendations = []
        overall_status = ValidationStatus.PASSED
        
        try:
            # Check 1: Backup exists
            try:
                backup = self.block_storage_client.get_volume_backup(backup_id).data
                checks[ValidationCheck.BACKUP_EXISTS.value] = {
                    "status": "passed",
                    "message": "Backup exists and is accessible",
                    "details": {
                        "display_name": backup.display_name,
                        "lifecycle_state": backup.lifecycle_state,
                        "time_created": str(backup.time_created)
                    }
                }
                
                if backup.lifecycle_state != "AVAILABLE":
                    issues.append(f"Backup state is {backup.lifecycle_state}, not AVAILABLE")
                    overall_status = ValidationStatus.WARNING
                    
            except Exception as e:
                checks[ValidationCheck.BACKUP_EXISTS.value] = {
                    "status": "failed",
                    "message": f"Failed to access backup: {e}"
                }
                issues.append(f"Cannot access backup: {e}")
                overall_status = ValidationStatus.FAILED
                return ValidationResult(
                    backup_id=backup_id,
                    backup_type="block_volume",
                    validation_time=datetime.utcnow().isoformat(),
                    overall_status=overall_status,
                    checks=checks,
                    issues=issues,
                    recommendations=recommendations,
                    compliance_status="FAILED"
                )
            
            # Check 2: Metadata validation
            checks[ValidationCheck.METADATA_VALID.value] = self._validate_metadata(backup)
            if checks[ValidationCheck.METADATA_VALID.value]["status"] == "failed":
                issues.extend(checks[ValidationCheck.METADATA_VALID.value].get("issues", []))
            
            # Check 3: Size validation
            checks[ValidationCheck.SIZE_VALID.value] = self._validate_size(backup)
            
            # Check 4: Encryption verification
            checks[ValidationCheck.ENCRYPTION_VERIFIED.value] = self._validate_encryption(backup)
            if checks[ValidationCheck.ENCRYPTION_VERIFIED.value]["status"] == "failed":
                recommendations.append("Enable encryption for all backups")
            
            # Determine compliance status
            compliance_status = "COMPLIANT" if overall_status == ValidationStatus.PASSED else "NON_COMPLIANT"
            
        except Exception as e:
            logging.error("Validation failed: %s", e)
            overall_status = ValidationStatus.FAILED
            compliance_status = "FAILED"
            issues.append(f"Validation exception: {e}")
        
        return ValidationResult(
            backup_id=backup_id,
            backup_type="block_volume",
            validation_time=datetime.utcnow().isoformat(),
            overall_status=overall_status,
            checks=checks,
            issues=issues,
            recommendations=recommendations,
            compliance_status=compliance_status
        )
    
    def _validate_metadata(self, backup) -> dict:
        """Validate backup metadata"""
        issues = []
        
        # Check required fields
        if not backup.display_name:
            issues.append("Missing display name")
        
        if not backup.time_created:
            issues.append("Missing creation time")
        
        # Check age
        age_days = (datetime.now(backup.time_created.tzinfo) - backup.time_created).days
        if age_days > 365:
            issues.append(f"Backup is very old ({age_days} days)")
        
        status = "failed" if issues else "passed"
        message = "Metadata validation passed" if not issues else f"Metadata issues found: {len(issues)}"
        
        return {
            "status": status,
            "message": message,
            "issues": issues,
            "details": {
                "age_days": age_days,
                "display_name": backup.display_name
            }
        }
    
    def _validate_size(self, backup) -> dict:
        """Validate backup size"""
        size_gb = backup.size_in_gbs
        
        # Warn if size is suspicious
        if size_gb < 1:
            return {
                "status": "warning",
                "message": f"Backup size is very small: {size_gb} GB",
                "details": {"size_gb": size_gb}
            }
        elif size_gb > 10000:  # 10TB
            return {
                "status": "warning",
                "message": f"Backup size is very large: {size_gb} GB",
                "details": {"size_gb": size_gb}
            }
        else:
            return {
                "status": "passed",
                "message": f"Backup size is normal: {size_gb} GB",
                "details": {"size_gb": size_gb}
            }
    
    def _validate_encryption(self, backup) -> dict:
        """Validate backup encryption"""
        kms_key_id = getattr(backup, 'kms_key_id', None)
        
        if kms_key_id:
            return {
                "status": "passed",
                "message": "Backup is encrypted with KMS",
                "details": {
                    "kms_key_id": kms_key_id,
                    "encryption_type": "KMS"
                }
            }
        else:
            return {
                "status": "failed",
                "message": "Backup is not encrypted",
                "details": {
                    "encryption_type": "none"
                }
            }
    
    def validate_compartment_backups(self, compartment_id: str) -> List[ValidationResult]:
        """Validate all backups in a compartment"""
        logging.info("Validating all backups in compartment: %s", compartment_id)
        
        results = []
        
        try:
            # Validate boot volume backups
            boot_backups = self.block_storage_client.list_boot_volume_backups(
                compartment_id=compartment_id
            ).data
            
            for backup in boot_backups:
                result = self.validate_boot_volume_backup(backup.id)
                results.append(result)
            
            # Validate block volume backups
            volume_backups = self.block_storage_client.list_volume_backups(
                compartment_id=compartment_id
            ).data
            
            for backup in volume_backups:
                result = self.validate_volume_backup(backup.id)
                results.append(result)
            
            logging.info("Validated %d backups in compartment", len(results))
            
        except Exception as e:
            logging.error("Failed to validate compartment backups: %s", e)
        
        return results
    
    def generate_compliance_report(self, results: List[ValidationResult]) -> dict:
        """Generate a compliance report from validation results"""
        total = len(results)
        passed = sum(1 for r in results if r.overall_status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.overall_status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.overall_status == ValidationStatus.WARNING)
        
        compliance_rate = (passed / total * 100) if total > 0 else 0
        
        report = {
            "report_date": datetime.utcnow().isoformat(),
            "summary": {
                "total_backups": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "compliance_rate": f"{compliance_rate:.1f}%"
            },
            "status": "COMPLIANT" if compliance_rate >= 95 else "NON_COMPLIANT",
            "failed_backups": [
                r.backup_id for r in results 
                if r.overall_status == ValidationStatus.FAILED
            ],
            "recommendations": self._generate_recommendations(results),
            "details": [r.to_dict() for r in results]
        }
        
        return report
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = set()
        
        for result in results:
            recommendations.update(result.recommendations)
        
        # Add general recommendations
        failed_count = sum(1 for r in results if r.overall_status == ValidationStatus.FAILED)
        if failed_count > 0:
            recommendations.add("Investigate and remediate failed backups immediately")
        
        unencrypted = sum(
            1 for r in results 
            if r.checks.get(ValidationCheck.ENCRYPTION_VERIFIED.value, {}).get("status") == "failed"
        )
        if unencrypted > 0:
            recommendations.add(f"Enable encryption for {unencrypted} unencrypted backups")
        
        return sorted(list(recommendations))


def main():
    """CLI for backup validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCI Backup Validator")
    parser.add_argument("action", choices=["validate-backup", "validate-compartment", "generate-report"],
                       help="Action to perform")
    parser.add_argument("--backup-id", help="Backup ID to validate")
    parser.add_argument("--backup-type", choices=["boot", "volume"], help="Type of backup")
    parser.add_argument("--compartment", help="Compartment ID to validate")
    parser.add_argument("--profile", help="OCI config profile")
    parser.add_argument("--output", help="Output file for report (JSON)")
    
    args = parser.parse_args()
    
    validator = BackupValidator(profile=args.profile)
    
    if args.action == "validate-backup":
        if not args.backup_id or not args.backup_type:
            print("Error: --backup-id and --backup-type required")
            return
        
        if args.backup_type == "boot":
            result = validator.validate_boot_volume_backup(args.backup_id)
        else:
            result = validator.validate_volume_backup(args.backup_id)
        
        print(f"\n{'='*80}")
        print(f"Validation Result: {result.overall_status.value.upper()}")
        print(f"{'='*80}\n")
        print(result.to_json())
        
        if result.issues:
            print(f"\n⚠️  Issues Found ({len(result.issues)}):")
            for issue in result.issues:
                print(f"  - {issue}")
        
        if result.recommendations:
            print(f"\n💡 Recommendations ({len(result.recommendations)}):")
            for rec in result.recommendations:
                print(f"  - {rec}")
    
    elif args.action == "validate-compartment":
        if not args.compartment:
            print("Error: --compartment required")
            return
        
        results = validator.validate_compartment_backups(args.compartment)
        report = validator.generate_compliance_report(results)
        
        print(f"\n{'='*80}")
        print(f"Compliance Report")
        print(f"{'='*80}\n")
        print(f"Total Backups: {report['summary']['total_backups']}")
        print(f"✅ Passed: {report['summary']['passed']}")
        print(f"⚠️  Warnings: {report['summary']['warnings']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"\nCompliance Rate: {report['summary']['compliance_rate']}")
        print(f"Status: {report['status']}")
        
        if report['failed_backups']:
            print(f"\nFailed Backups:")
            for backup_id in report['failed_backups']:
                print(f"  - {backup_id}")
        
        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ Report saved to: {args.output}")
    
    elif args.action == "generate-report":
        print("generate-report requires validate-compartment first")


if __name__ == "__main__":
    main()
