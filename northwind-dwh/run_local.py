#!/usr/bin/env python3
"""Полный цикл без Docker: локальный PostgreSQL, база Northwind и хранилище-звезда."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from shutil import which

ROOT = Path(__file__).resolve().parent
PGHOST = os.environ.get("PGHOST", "127.0.0.1")
ADMIN_USER = os.environ.get("PGUSER", "postgres")
ADMIN_PASS = os.environ.get("PGADMIN_PASSWORD", "postgres")
DWH_USER = os.environ.get("DWH_USER", "dwh")
DWH_PASS = os.environ.get("DWH_PASSWORD", "dwh")

CANDIDATES = [
    "psql",
    r"C:\Program Files\PostgreSQL\17\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
]


def find_psql() -> str:
    for candidate in CANDIDATES:
        if candidate == "psql":
            found = which("psql")
            if found:
                return found
        elif Path(candidate).is_file():
            return candidate
    raise SystemExit("psql не найден. Установите PostgreSQL или добавьте psql в PATH.")


def run_psql(psql: str, user: str, password: str, database: str, *args: str) -> str:
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    env["PGCLIENTENCODING"] = "UTF8"
    cmd = [psql, "-U", user, "-h", PGHOST, "-d", database, "-v", "ON_ERROR_STOP=1", *args]
    completed = subprocess.run(
        cmd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def ensure_db(psql: str, name: str) -> None:
    exists = run_psql(
        psql, ADMIN_USER, ADMIN_PASS, "postgres", "-tAc",
        f"SELECT 1 FROM pg_database WHERE datname='{name}'",
    ).strip()
    if exists != "1":
        run_psql(
            psql, ADMIN_USER, ADMIN_PASS, "postgres",
            "-c", f"CREATE DATABASE {name} OWNER {DWH_USER};",
        )


def main() -> None:
    psql = find_psql()
    print(">>> 1/6 Роль dwh ...")
    role_sql = f"""
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{DWH_USER}') THEN
    CREATE ROLE {DWH_USER} LOGIN PASSWORD '{DWH_PASS}' SUPERUSER;
  ELSE
    ALTER ROLE {DWH_USER} WITH LOGIN PASSWORD '{DWH_PASS}' SUPERUSER;
  END IF;
END $$;
"""
    run_psql(psql, ADMIN_USER, ADMIN_PASS, "postgres", "-c", role_sql)

    print(">>> 2/6 База-источник northwind ...")
    ensure_db(psql, "northwind")
    loaded = run_psql(
        psql, ADMIN_USER, ADMIN_PASS, "northwind", "-tAc",
        "SELECT to_regclass('public.orders') IS NOT NULL",
    ).strip()
    if loaded != "t":
        print(">>> Загрузка официального скрипта Northwind ...")
        run_psql(
            psql, ADMIN_USER, ADMIN_PASS, "northwind",
            "-f", str(ROOT / "data" / "raw" / "northwind.sql"),
        )
    run_psql(
        psql, ADMIN_USER, ADMIN_PASS, "postgres",
        "-c", f"ALTER DATABASE northwind OWNER TO {DWH_USER};",
    )
    run_psql(
        psql, ADMIN_USER, ADMIN_PASS, "northwind",
        "-c",
        f"GRANT ALL ON SCHEMA public TO {DWH_USER}; "
        f"GRANT ALL ON ALL TABLES IN SCHEMA public TO {DWH_USER};",
    )

    print(">>> 3/6 База хранилища ...")
    ensure_db(psql, "northwind_dwh")

    print(">>> 4/6 Схема звезды ...")
    run_psql(psql, DWH_USER, DWH_PASS, "northwind_dwh", "-f", str(ROOT / "dwh" / "schema.sql"))

    print(">>> 5/6 ETL ...")
    run_psql(psql, DWH_USER, DWH_PASS, "northwind_dwh", "-f", str(ROOT / "dwh" / "etl.sql"))

    print(">>> 6/6 Витрина ...")
    run_psql(
        psql, DWH_USER, DWH_PASS, "northwind_dwh",
        "-f", str(ROOT / "dwh" / "reports" / "metrics.sql"),
    )

    print("\nГотово. Проверка:")
    print(run_psql(
        psql, DWH_USER, DWH_PASS, "northwind_dwh", "-c",
        "SELECT (SELECT count(*) FROM fact_order_line) AS fact_rows, "
        "(SELECT round(sum(line_total),2) FROM fact_order_line) AS revenue;",
    ))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.stderr.write((exc.stderr or "") + (exc.stdout or ""))
        raise SystemExit(exc.returncode or 1)
