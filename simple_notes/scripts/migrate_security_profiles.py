import argparse
from datetime import datetime
from sqlalchemy import text
from ..extensions import db

"""
Migration script to enforce NOT NULL on security_profiles.question and security_profiles.answer_hash.
- Scans existing data and reports NULL/empty counts.
- For SQLite: recreates table with NOT NULL constraints and backfills NULLs to empty strings.
- For MySQL: alters columns to NOT NULL.
Run: python -m diary_app.scripts.migrate_security_profiles --apply
"""

def scan():
    engine = db.engine
    with engine.connect() as conn:
        dialect = engine.dialect.name
        stats = {}
        if dialect == 'sqlite':
            q = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE question IS NULL")).scalar() or 0
            a = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE answer_hash IS NULL")).scalar() or 0
            qe = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE question = ''")).scalar() or 0
            ae = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE answer_hash = ''")).scalar() or 0
        else:
            # MySQL treats empty string similarly, but count explicitly
            q = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE question IS NULL")).scalar() or 0
            a = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE answer_hash IS NULL")).scalar() or 0
            qe = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE question = ''")).scalar() or 0
            ae = conn.execute(text("SELECT COUNT(*) FROM security_profiles WHERE answer_hash = ''")).scalar() or 0
        stats['null_question'] = q
        stats['null_answer_hash'] = a
        stats['empty_question'] = qe
        stats['empty_answer_hash'] = ae
        return dialect, stats


def apply_migration():
    engine = db.engine
    dialect, stats = scan()
    print(f"Dialect: {dialect}")
    print(f"Stats: {stats}")
    with engine.connect() as conn:
        if dialect == 'sqlite':
            # Recreate table with NOT NULL constraints
            conn.exec_driver_sql("PRAGMA foreign_keys=OFF;")
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS security_profiles_new (
                  id INTEGER PRIMARY KEY,
                  user_id INTEGER UNIQUE NOT NULL,
                  question TEXT NOT NULL,
                  answer_hash TEXT NOT NULL,
                  failed_count INTEGER DEFAULT 0 NOT NULL,
                  locked_until DATETIME,
                  FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )
            # Copy and backfill NULLs to empty strings to satisfy NOT NULL
            conn.exec_driver_sql(
                """
                INSERT INTO security_profiles_new (id, user_id, question, answer_hash, failed_count, locked_until)
                SELECT id, user_id, COALESCE(question, ''), COALESCE(answer_hash, ''), COALESCE(failed_count, 0), locked_until
                FROM security_profiles;
                """
            )
            # Replace table
            conn.exec_driver_sql("DROP TABLE security_profiles;")
            conn.exec_driver_sql("ALTER TABLE security_profiles_new RENAME TO security_profiles;")
            conn.commit()
            conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
            print("SQLite migration applied: NOT NULL enforced, NULLs backfilled to empty strings.")
        elif dialect in ('mysql', 'mysql+pymysql'):
            # MySQL modify columns to NOT NULL
            conn.exec_driver_sql(
                """
                ALTER TABLE security_profiles
                MODIFY question VARCHAR(255) NOT NULL,
                MODIFY answer_hash VARCHAR(255) NOT NULL,
                MODIFY failed_count INTEGER NOT NULL DEFAULT 0;
                """
            )
            print("MySQL migration applied: columns set to NOT NULL.")
        else:
            raise RuntimeError(f"Unsupported dialect for migration: {dialect}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate security_profiles to NOT NULL constraints')
    parser.add_argument('--apply', action='store_true', help='Apply migration changes')
    args = parser.parse_args()

    from .. import create_app
    app = create_app()
    with app.app_context():
        dialect, stats = scan()
        print(f"Dialect: {dialect}")
        print(f"Current NULL/empty stats: {stats}")
        if args.apply:
            apply_migration()
            dialect, stats = scan()
            print(f"Post-migration stats: {stats}")
        else:
            print('Dry run complete. Re-run with --apply to perform migration.')