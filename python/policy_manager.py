#!/usr/bin/env python3
"""
policy_manager.py - Backup Policy Management for OCI DataProtect MVP

Manages backup policies including scheduling, retention, and enforcement.
Demonstrates enterprise-grade policy automation.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import oci

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class BackupFrequency(Enum):
    """Backup schedule frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RetentionClass(Enum):
    """Retention classification for compliance"""
    STANDARD = "standard"      # 30 days
    EXTENDED = "extended"      # 90 days
    LONG_TERM = "long_term"    # 365 days
    PERMANENT = "permanent"    # Never delete


@dataclass
class BackupPolicy:
    """Backup policy definition"""
    policy_id: str
    name: str
    description: str
    frequency: BackupFrequency
    retention_days: int
    retention_class: RetentionClass
    enabled: bool = True
    schedule: str = "0 2 * * *"  # Cron expression (default: 2 AM daily)
    validate_backups: bool = True
    encrypt_backups: bool = True
    immutable_backups: bool = False
    target_compartments: List[str] = None
    target_tags: Dict[str, str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.target_compartments is None:
            self.target_compartments = []
        if self.target_tags is None:
            self.target_tags = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert policy to dictionary for storage"""
        data = asdict(self)
        data['frequency'] = self.frequency.value
        data['retention_class'] = self.retention_class.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BackupPolicy':
        """Create policy from dictionary"""
        data['frequency'] = BackupFrequency(data['frequency'])
        data['retention_class'] = RetentionClass(data['retention_class'])
        return cls(**data)


class PolicyManager:
    """Manages backup policies and enforcement"""
    
    def __init__(self, config_path: str = "/etc/oci-backup/policies.json"):
        self.config_path = config_path
        self.policies: Dict[str, BackupPolicy] = {}
        self.load_policies()
        logging.info("PolicyManager initialized with %d policies", len(self.policies))
    
    def load_policies(self):
        """Load policies from configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                for policy_data in data.get('policies', []):
                    policy = BackupPolicy.from_dict(policy_data)
                    self.policies[policy.policy_id] = policy
            logging.info("Loaded %d policies from %s", len(self.policies), self.config_path)
        except FileNotFoundError:
            logging.warning("Policy file not found: %s. Starting with empty policies.", self.config_path)
            self.policies = {}
        except Exception as e:
            logging.error("Error loading policies: %s", e)
            self.policies = {}
    
    def save_policies(self):
        """Save policies to configuration file"""
        try:
            data = {
                'policies': [p.to_dict() for p in self.policies.values()],
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info("Saved %d policies to %s", len(self.policies), self.config_path)
        except Exception as e:
            logging.error("Error saving policies: %s", e)
            raise
    
    def create_policy(self, policy: BackupPolicy) -> BackupPolicy:
        """Create a new backup policy"""
        if policy.policy_id in self.policies:
            raise ValueError(f"Policy {policy.policy_id} already exists")
        
        self.policies[policy.policy_id] = policy
        self.save_policies()
        logging.info("Created policy: %s (%s)", policy.name, policy.policy_id)
        return policy
    
    def update_policy(self, policy_id: str, updates: dict) -> BackupPolicy:
        """Update an existing policy"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")
        
        policy = self.policies[policy_id]
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_at = datetime.utcnow().isoformat()
        self.save_policies()
        logging.info("Updated policy: %s", policy_id)
        return policy
    
    def delete_policy(self, policy_id: str):
        """Delete a policy"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy {policy_id} not found")
        
        del self.policies[policy_id]
        self.save_policies()
        logging.info("Deleted policy: %s", policy_id)
    
    def get_policy(self, policy_id: str) -> Optional[BackupPolicy]:
        """Get a specific policy"""
        return self.policies.get(policy_id)
    
    def list_policies(self, enabled_only: bool = False) -> List[BackupPolicy]:
        """List all policies"""
        policies = list(self.policies.values())
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        return policies
    
    def get_policies_for_compartment(self, compartment_id: str) -> List[BackupPolicy]:
        """Get all policies applicable to a compartment"""
        return [
            p for p in self.policies.values()
            if compartment_id in p.target_compartments and p.enabled
        ]
    
    def get_policies_by_tags(self, tags: Dict[str, str]) -> List[BackupPolicy]:
        """Get policies matching specific tags"""
        matching_policies = []
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            # Check if all policy tags match
            if all(tags.get(k) == v for k, v in policy.target_tags.items()):
                matching_policies.append(policy)
        return matching_policies
    
    def get_retention_days(self, retention_class: RetentionClass) -> int:
        """Get retention days for a retention class"""
        retention_map = {
            RetentionClass.STANDARD: 30,
            RetentionClass.EXTENDED: 90,
            RetentionClass.LONG_TERM: 365,
            RetentionClass.PERMANENT: -1  # Never delete
        }
        return retention_map.get(retention_class, 30)
    
    def enforce_retention(self, compartment_id: str, profile: str = None):
        """Enforce retention policies by cleaning up old backups"""
        try:
            # Load OCI clients
            if profile:
                config = oci.config.from_file(profile_name=profile)
                signer = None
            else:
                try:
                    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                    config = {}
                except Exception:
                    config = oci.config.from_file()
                    signer = None
            
            block_storage = oci.core.BlockstorageClient(config, signer=signer)
            
            # Get policies for this compartment
            policies = self.get_policies_for_compartment(compartment_id)
            logging.info("Enforcing retention for %d policies", len(policies))
            
            for policy in policies:
                if policy.retention_class == RetentionClass.PERMANENT:
                    logging.info("Skipping retention for permanent policy: %s", policy.name)
                    continue
                
                retention_days = policy.retention_days
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # List backups older than retention period
                boot_backups = block_storage.list_boot_volume_backups(
                    compartment_id=compartment_id
                ).data
                
                volume_backups = block_storage.list_volume_backups(
                    compartment_id=compartment_id
                ).data
                
                deleted_count = 0
                
                # Delete old boot volume backups
                for backup in boot_backups:
                    backup_date = backup.time_created
                    if backup_date < cutoff_date:
                        try:
                            block_storage.delete_boot_volume_backup(backup.id)
                            logging.info("Deleted old boot backup: %s (created: %s)", 
                                       backup.id, backup_date)
                            deleted_count += 1
                        except Exception as e:
                            logging.error("Failed to delete boot backup %s: %s", backup.id, e)
                
                # Delete old volume backups
                for backup in volume_backups:
                    backup_date = backup.time_created
                    if backup_date < cutoff_date:
                        try:
                            block_storage.delete_volume_backup(backup.id)
                            logging.info("Deleted old volume backup: %s (created: %s)", 
                                       backup.id, backup_date)
                            deleted_count += 1
                        except Exception as e:
                            logging.error("Failed to delete volume backup %s: %s", backup.id, e)
                
                logging.info("Policy %s: Deleted %d old backups", policy.name, deleted_count)
            
        except Exception as e:
            logging.error("Error enforcing retention: %s", e)
            raise


def create_default_policies() -> List[BackupPolicy]:
    """Create default backup policies for common scenarios"""
    policies = [
        # Production - Daily backups with extended retention
        BackupPolicy(
            policy_id="prod-daily",
            name="Production Daily Backup",
            description="Daily backups for production workloads with 90-day retention",
            frequency=BackupFrequency.DAILY,
            retention_days=90,
            retention_class=RetentionClass.EXTENDED,
            schedule="0 2 * * *",  # 2 AM daily
            validate_backups=True,
            encrypt_backups=True,
            immutable_backups=True,
            target_tags={"Environment": "Production"}
        ),
        
        # Development - Weekly backups with standard retention
        BackupPolicy(
            policy_id="dev-weekly",
            name="Development Weekly Backup",
            description="Weekly backups for development environments",
            frequency=BackupFrequency.WEEKLY,
            retention_days=30,
            retention_class=RetentionClass.STANDARD,
            schedule="0 3 * * 0",  # 3 AM every Sunday
            validate_backups=False,
            encrypt_backups=True,
            immutable_backups=False,
            target_tags={"Environment": "Development"}
        ),
        
        # Critical - Hourly backups with long-term retention
        BackupPolicy(
            policy_id="critical-hourly",
            name="Critical System Hourly Backup",
            description="Hourly backups for mission-critical systems",
            frequency=BackupFrequency.HOURLY,
            retention_days=365,
            retention_class=RetentionClass.LONG_TERM,
            schedule="0 * * * *",  # Every hour
            validate_backups=True,
            encrypt_backups=True,
            immutable_backups=True,
            target_tags={"Criticality": "Mission-Critical"}
        ),
        
        # Compliance - Monthly backups with permanent retention
        BackupPolicy(
            policy_id="compliance-monthly",
            name="Compliance Archive",
            description="Monthly backups for compliance with permanent retention",
            frequency=BackupFrequency.MONTHLY,
            retention_days=-1,
            retention_class=RetentionClass.PERMANENT,
            schedule="0 4 1 * *",  # 4 AM on 1st of month
            validate_backups=True,
            encrypt_backups=True,
            immutable_backups=True,
            target_tags={"Compliance": "Required"}
        )
    ]
    return policies


def main():
    """CLI for policy management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OCI Backup Policy Manager")
    parser.add_argument("action", choices=["list", "create-defaults", "enforce", "show"],
                       help="Action to perform")
    parser.add_argument("--policy-id", help="Policy ID for show action")
    parser.add_argument("--compartment", help="Compartment ID for enforce action")
    parser.add_argument("--profile", help="OCI config profile")
    
    args = parser.parse_args()
    
    manager = PolicyManager()
    
    if args.action == "list":
        policies = manager.list_policies()
        print(f"\n{'='*80}")
        print(f"Total Policies: {len(policies)}")
        print(f"{'='*80}\n")
        
        for policy in policies:
            status = "✅ Enabled" if policy.enabled else "❌ Disabled"
            print(f"Policy: {policy.name} ({policy.policy_id})")
            print(f"  Status: {status}")
            print(f"  Frequency: {policy.frequency.value}")
            print(f"  Retention: {policy.retention_days} days ({policy.retention_class.value})")
            print(f"  Schedule: {policy.schedule}")
            print(f"  Immutable: {'Yes' if policy.immutable_backups else 'No'}")
            print(f"  Validation: {'Yes' if policy.validate_backups else 'No'}")
            print(f"  Created: {policy.created_at}")
            print()
    
    elif args.action == "create-defaults":
        default_policies = create_default_policies()
        for policy in default_policies:
            try:
                manager.create_policy(policy)
                print(f"✅ Created policy: {policy.name}")
            except ValueError as e:
                print(f"⚠️  {e}")
        print(f"\n{len(default_policies)} default policies processed.")
    
    elif args.action == "show":
        if not args.policy_id:
            print("Error: --policy-id required for show action")
            return
        
        policy = manager.get_policy(args.policy_id)
        if not policy:
            print(f"Policy {args.policy_id} not found")
            return
        
        print(f"\n{'='*80}")
        print(f"Policy Details: {policy.name}")
        print(f"{'='*80}\n")
        print(json.dumps(policy.to_dict(), indent=2))
    
    elif args.action == "enforce":
        if not args.compartment:
            print("Error: --compartment required for enforce action")
            return
        
        print(f"Enforcing retention policies for compartment: {args.compartment}")
        manager.enforce_retention(args.compartment, args.profile)
        print("✅ Retention enforcement complete")


if __name__ == "__main__":
    main()
