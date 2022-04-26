"""Database migration management."""
import os, logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class Migration:
    """Single database migration."""

    def __init__(self, version: str, name: str, up_sql: str, down_sql: str):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql

class MigrationManager:
    """Manage database schema migrations."""

    def __init__(self, db_manager):
        self.db = db_manager
        self.migrations: List[Migration] = []
        self._ensure_migration_table()

    def _ensure_migration_table(self):
        """Create migrations tracking table if not exists."""
        with self.db.session() as session:
            session.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(20) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

    def register(self, migration: Migration):
        """Register a migration."""
        self.migrations.append(migration)

    def get_applied(self) -> List[str]:
        """Get list of applied migration versions."""
        with self.db.session() as session:
            result = session.execute("SELECT version FROM schema_migrations ORDER BY version")
            return [row[0] for row in result]

    def migrate_up(self) -> List[str]:
        """Apply all pending migrations."""
        applied = set(self.get_applied())
        pending = [m for m in self.migrations if m.version not in applied]
        applied_names = []
        for migration in sorted(pending, key=lambda m: m.version):
            logger.info("Applying migration %s: %s", migration.version, migration.name)
            with self.db.session() as session:
                session.execute(migration.up_sql)
                session.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                    (migration.version, migration.name),
                )
            applied_names.append(migration.name)
            logger.info("Applied: %s", migration.name)
        return applied_names

    def migrate_down(self, version: str) -> bool:
        """Rollback to a specific version."""
        for migration in reversed(sorted(self.migrations, key=lambda m: m.version)):
            if migration.version <= version:
                break
            logger.info("Rolling back migration %s: %s", migration.version, migration.name)
            with self.db.session() as session:
                session.execute(migration.down_sql)
                session.execute("DELETE FROM schema_migrations WHERE version = %s", (migration.version,))
        return True
