"""Consistent copy of the SQLite database while the site keeps running.

    python manage.py backup_db                 -> <database folder>/backups/db-YYYYmmdd-HHMMSS.sqlite3
    python manage.py backup_db --keep 14       -> also delete all but the 14 newest copies
    python manage.py backup_db --output /path/file.sqlite3

Docker: docker compose exec ncf python manage.py backup_db   (copies land in the ncf-data volume, /data/backups)
Do not copy db.sqlite3 with cp while the site runs: with the WAL journal the copy can be incomplete.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Make a consistent backup copy of the SQLite database (safe while the site is running)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help="Target file. Default: <database folder>/backups/db-<timestamp>.sqlite3",
        )
        parser.add_argument(
            "--keep",
            type=int,
            default=0,
            help="Keep only the N newest copies in the default folder (0 = keep all).",
        )

    def handle(self, *args, output=None, keep=0, **options):
        source = Path(settings.DATABASES["default"]["NAME"])
        if not source.exists():
            raise CommandError(f"Database file not found: {source}")
        backup_dir = source.parent / "backups"
        target = (
            Path(output) if output else backup_dir / f"db-{datetime.now():%Y%m%d-%H%M%S}.sqlite3"
        )
        target.parent.mkdir(parents=True, exist_ok=True)

        src = sqlite3.connect(source)
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        self.stdout.write(self.style.SUCCESS(f"Backup written: {target}"))

        if keep > 0 and not output:
            old = sorted(backup_dir.glob("db-*.sqlite3"))[:-keep]
            for path in old:
                path.unlink()
            if old:
                self.stdout.write(f"Deleted {len(old)} old backup(s).")
