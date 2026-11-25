import sqlite3
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class BackupDbCommandTest(SimpleTestCase):
    def test_copies_database_and_rotates(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp, "db.sqlite3")
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE t (x INTEGER)")
                conn.execute("INSERT INTO t VALUES (42)")
            databases = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": db}}
            with override_settings(DATABASES=databases):
                for name in ("db-20000101-000000.sqlite3", "db-20000102-000000.sqlite3"):
                    Path(tmp, "backups").mkdir(exist_ok=True)
                    Path(tmp, "backups", name).write_bytes(b"old")
                call_command("backup_db", "--keep", "1", stdout=StringIO())
            copies = sorted(Path(tmp, "backups").glob("db-*.sqlite3"))
            self.assertEqual(len(copies), 1)
            with sqlite3.connect(copies[0]) as conn:
                self.assertEqual(conn.execute("SELECT x FROM t").fetchone(), (42,))
