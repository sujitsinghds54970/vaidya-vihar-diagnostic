"""
Automated Backup Service for VaidyaVihar Diagnostic ERP
Supports SQLite and PostgreSQL databases
"""

import os
import shutil
import gzip
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import logging
import schedule
import threading

logger = logging.getLogger(__name__)


@dataclass
class BackupConfig:
    """Backup configuration settings"""
    backup_dir: str = "./backups"
    sqlite_db_path: str = "./vaidya_vihar.db"
    pg_db_url: Optional[str] = None  # PostgreSQL connection string
    keep_daily_backups: int = 7
    keep_weekly_backups: int = 4
    keep_monthly_backups: int = 12
    encrypt_backups: bool = False
    upload_to_cloud: bool = False
    cloud_provider: str = "aws"  # aws, gcp, azure


class BackupService:
    """Automated backup service for database and files"""
    
    def __init__(self, config: Optional[BackupConfig] = None):
        self.config = config or BackupConfig()
        self.backup_dir = Path(self.config.backup_dir)
        self._ensure_backup_dir()
        
    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        (self.backup_dir / "daily").mkdir(exist_ok=True)
        (self.backup_dir / "weekly").mkdir(exist=True)
        (self.backup_dir / "monthly").mkdir(exist_ok=True)
        (self.backup_dir / "logs").mkdir(exist_ok=True)
        logger.info(f"Backup directory created: {self.backup_dir}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for backup file naming"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def backup_sqlite(self) -> str:
        """Create a backup of SQLite database"""
        timestamp = self._get_timestamp()
        backup_path = self.backup_dir / "daily" / f"vaidya_vihar_{timestamp}.db.gz"
        
        try:
            # Create temporary copy to backup (to avoid locking issues)
            temp_backup = self.backup_dir / f"temp_backup_{timestamp}.db"
            
            # Copy database file
            shutil.copy2(self.config.sqlite_db_path, temp_backup)
            
            # Compress the backup
            with open(temp_backup, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove temporary file
            temp_backup.unlink()
            
            # Create symbolic link to latest backup
            latest_link = self.backup_dir / "daily" / "latest.db.gz"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(backup_path.name)
            
            logger.info(f"SQLite backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Failed to create SQLite backup: {e}")
            raise
    
    def backup_postgres(self) -> str:
        """Create a backup of PostgreSQL database"""
        if not self.config.pg_db_url:
            logger.warning("PostgreSQL URL not configured")
            return ""
        
        timestamp = self._get_timestamp()
        backup_path = self.backup_dir / "daily" / f"vaidya_vihar_{timestamp}.sql.gz"
        
        try:
            # Use pg_dump to create backup
            import subprocess
            
            # Build command
            cmd = [
                'pg_dump',
                '--format=custom',
                '--compress=9',
                '--dbname', self.config.pg_db_url.split('/')[-1],
                '--file', str(backup_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"pg_dump failed: {result.stderr}")
                raise Exception(result.stderr)
            
            logger.info(f"PostgreSQL backup created: {backup_path}")
            return str(backup_path)
            
        except FileNotFoundError:
            logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            raise
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL backup: {e}")
            raise
    
    def backup_all(self) -> List[str]:
        """Create backup of all databases"""
        backups = []
        
        # Backup SQLite if exists
        if Path(self.config.sqlite_db_path).exists():
            try:
                backup = self.backup_sqlite()
                backups.append(backup)
            except Exception as e:
                logger.error(f"SQLite backup failed: {e}")
        
        # Backup PostgreSQL if configured
        if self.config.pg_db_url:
            try:
                backup = self.backup_postgres()
                backups.append(backup)
            except Exception as e:
                logger.error(f"PostgreSQL backup failed: {e}")
        
        return backups
    
    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        now = datetime.now()
        
        # Clean daily backups
        daily_dir = self.backup_dir / "daily"
        for backup in daily_dir.glob("vaidya_vihar_*.db.gz"):
            # Skip latest backup
            if backup.name == "latest.db.gz":
                continue
                
            try:
                date_str = backup.name.replace("vaidya_vihar_", "").replace(".db.gz", "")
                backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if (now - backup_date).days > self.config.keep_daily_backups:
                    backup.unlink()
                    logger.info(f"Removed old daily backup: {backup}")
            except ValueError:
                continue
        
        # Clean weekly backups (keep 4 weeks)
        weekly_dir = self.backup_dir / "weekly"
        for backup in weekly_dir.glob("vaidya_vihar_*.sql.gz"):
            try:
                date_str = backup.name.replace("vaidya_vihar_", "").replace(".sql.gz", "")
                backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if (now - backup_date).days > (self.config.keep_weekly_backups * 7):
                    backup.unlink()
                    logger.info(f"Removed old weekly backup: {backup}")
            except ValueError:
                continue
        
        # Clean monthly backups (keep 12 months)
        monthly_dir = self.backup_dir / "monthly"
        for backup in monthly_dir.glob("vaidya_vihar_*.sql.gz"):
            try:
                date_str = backup.name.replace("vaidya_vihar_", "").replace(".sql.gz", "")
                backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if (now - backup_date).days > (self.config.keep_monthly_backups * 30):
                    backup.unlink()
                    logger.info(f"Removed old monthly backup: {backup}")
            except ValueError:
                continue
    
    def rotate_weekly(self):
        """Create weekly backup by copying latest daily backup"""
        latest_backup = self.backup_dir / "daily" / "latest.db.gz"
        if latest_backup.exists():
            timestamp = self._get_timestamp()
            weekly_backup = self.backup_dir / "weekly" / f"vaidya_vihar_weekly_{timestamp}.sql.gz"
            shutil.copy2(latest_backup, weekly_backup)
            logger.info(f"Weekly backup created: {weekly_backup}")
    
    def rotate_monthly(self):
        """Create monthly backup by copying latest daily backup"""
        latest_backup = self.backup_dir / "daily" / "latest.db.gz"
        if latest_backup.exists():
            timestamp = self._get_timestamp()
            monthly_backup = self.backup_dir / "monthly" / f"vaidya_vihar_monthly_{timestamp}.sql.gz"
            shutil.copy2(latest_backup, monthly_backup)
            logger.info(f"Monthly backup created: {monthly_backup}")
    
    def restore_sqlite(self, backup_path: str) -> bool:
        """Restore SQLite database from backup"""
        backup = Path(backup_path)
        if not backup.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Remove old database
            Path(self.config.sqlite_db_path).unlink(missing_ok=True)
            
            # Decompress backup
            temp_restore = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_restore, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Move to original location
            shutil.move(temp_restore, self.config.sqlite_db_path)
            
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
    
    def get_backup_status(self) -> dict:
        """Get backup status and statistics"""
        status = {
            "last_backup": None,
            "backup_count": 0,
            "total_size": 0,
            "next_scheduled": None
        }
        
        # Find most recent backup
        latest = None
        for backup in self.backup_dir.rglob("vaidya_vihar_*.db.gz"):
            if backup.is_file():
                if latest is None or backup.stat().st_mtime > latest.stat().st_mtime:
                    latest = backup
        
        if latest:
            status["last_backup"] = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
            status["backup_count"] = len(list(self.backup_dir.rglob("vaidya_vihar_*.db.gz")))
            status["total_size"] = sum(
                f.stat().st_size 
                for f in self.backup_dir.rglob("vaidya_vihar_*.db.gz") 
                if f.is_file()
            )
        
        return status
    
    def upload_to_cloud(self, backup_path: str) -> bool:
        """Upload backup to cloud storage"""
        if not self.config.upload_to_cloud:
            return False
        
        # AWS S3 implementation
        if self.config.cloud_provider == "aws":
            try:
                import boto3
                s3 = boto3.client('s3')
                s3.upload_file(
                    backup_path,
                    'vaidya-vihar-backups',
                    f"backups/{Path(backup_path).name}"
                )
                logger.info(f"Backup uploaded to S3: {backup_path}")
                return True
            except ImportError:
                logger.warning("boto3 not installed. Cloud upload skipped.")
            except Exception as e:
                logger.error(f"Failed to upload to S3: {e}")
        
        return False


class BackupScheduler:
    """Scheduler for automated backup jobs"""
    
    def __init__(self, backup_service: BackupService):
        self.backup_service = backup_service
        self._scheduler_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self):
        """Start the backup scheduler"""
        # Schedule daily backup at 2 AM
        schedule.every().day.at("02:00").do(self.backup_service.backup_all)
        
        # Schedule weekly backup on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self.backup_service.rotate_weekly)
        
        # Schedule monthly backup on 1st at 4 AM
        schedule.every().month.do(self.backup_service.rotate_monthly)
        
        # Schedule cleanup daily at 5 AM
        schedule.every().day.at("05:00").do(self.backup_service.cleanup_old_backups)
        
        self._running = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        logger.info("Backup scheduler started")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self._running:
            schedule.run_pending()
            import time
            time.sleep(60)
    
    def stop(self):
        """Stop the backup scheduler"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Backup scheduler stopped")
    
    def run_now(self):
        """Run backup immediately"""
        backups = self.backup_service.backup_all()
        self.backup_service.cleanup_old_backups()
        return backups


# Global backup service instance
backup_service = BackupService()
backup_scheduler = BackupScheduler(backup_service)


def get_backup_service() -> BackupService:
    """Get the global backup service instance"""
    return backup_service


def get_backup_scheduler() -> BackupScheduler:
    """Get the global backup scheduler instance"""
    return backup_scheduler

