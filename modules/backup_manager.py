"""
SmartBill Pro - Database Backup & Restore Utility
Provides database backup, restore, and maintenance functions.
"""

import os
import shutil
import sqlite3
from datetime import datetime


class BackupManager:
    """Manages database backups and restoration."""

    def __init__(self, db_path, backup_dir=None):
        self.db_path = db_path
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(db_path), 'backups'
        )
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, label=None):
        """Create a timestamped backup of the database.

        Args:
            label: Optional label to include in the backup filename.

        Returns:
            str: Path to the created backup file.

        Raises:
            FileNotFoundError: If the source database doesn't exist.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        label_str = f"_{label}" if label else ""
        filename = f"smartbill_backup{label_str}_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, filename)

        # Use SQLite's backup API for a safe copy
        source = sqlite3.connect(self.db_path)
        dest = sqlite3.connect(backup_path)
        try:
            source.backup(dest)
        finally:
            dest.close()
            source.close()

        return backup_path

    def restore_backup(self, backup_path):
        """Restore the database from a backup file.

        Args:
            backup_path: Path to the backup file to restore from.

        Returns:
            str: Path to the pre-restore backup (safety copy).

        Raises:
            FileNotFoundError: If the backup file doesn't exist.
            sqlite3.DatabaseError: If the backup file is not a valid database.
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Validate the backup file is a valid SQLite database
        try:
            test_conn = sqlite3.connect(backup_path)
            test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
        except sqlite3.DatabaseError as e:
            raise sqlite3.DatabaseError(f"Invalid backup file: {e}")

        # Create a safety backup of the current database before restoring
        safety_backup = None
        if os.path.exists(self.db_path):
            safety_backup = self.create_backup(label="pre_restore")

        # Restore
        source = sqlite3.connect(backup_path)
        dest = sqlite3.connect(self.db_path)
        try:
            source.backup(dest)
        finally:
            dest.close()
            source.close()

        return safety_backup

    def list_backups(self):
        """List all available backup files.

        Returns:
            list: List of dicts with backup info (name, path, size, date).
        """
        backups = []

        if not os.path.exists(self.backup_dir):
            return backups

        for filename in sorted(os.listdir(self.backup_dir), reverse=True):
            if filename.endswith('.db') and filename.startswith('smartbill_backup'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'name': filename,
                    'path': filepath,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(
                        stat.st_mtime
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                })

        return backups

    def delete_backup(self, backup_path):
        """Delete a specific backup file.

        Args:
            backup_path: Path to the backup file to delete.

        Returns:
            bool: True if deleted successfully.
        """
        if os.path.exists(backup_path) and backup_path.startswith(self.backup_dir):
            os.remove(backup_path)
            return True
        return False

    def cleanup_old_backups(self, keep_count=10):
        """Remove old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep (default: 10).

        Returns:
            int: Number of backups deleted.
        """
        backups = self.list_backups()
        deleted = 0

        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                if self.delete_backup(backup['path']):
                    deleted += 1

        return deleted

    def get_db_stats(self):
        """Get database statistics.

        Returns:
            dict: Database statistics including size, table counts, etc.
        """
        stats = {}

        if os.path.exists(self.db_path):
            stats['size_bytes'] = os.path.getsize(self.db_path)
            stats['size_mb'] = round(stats['size_bytes'] / (1024 * 1024), 2)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get table row counts
            tables = ['Users', 'Menu', 'Orders', 'OrderItems', 'Settings']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f'{table.lower()}_count'] = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    stats[f'{table.lower()}_count'] = 0

            conn.close()

        stats['backup_count'] = len(self.list_backups())

        return stats


if __name__ == '__main__':
    # Quick CLI usage
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'database', 'smartbill.db')

    bm = BackupManager(db_path)

    if len(sys.argv) > 1:
        action = sys.argv[1]

        if action == 'backup':
            path = bm.create_backup()
            print(f"Backup created: {path}")

        elif action == 'list':
            backups = bm.list_backups()
            if backups:
                for b in backups:
                    print(f"  {b['name']}  ({b['size_mb']} MB)  {b['modified']}")
            else:
                print("  No backups found.")

        elif action == 'stats':
            stats = bm.get_db_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")

        elif action == 'cleanup':
            deleted = bm.cleanup_old_backups()
            print(f"  Removed {deleted} old backups.")

        else:
            print(f"Unknown action: {action}")
    else:
        print("Usage: python backup_manager.py [backup|list|stats|cleanup]")
