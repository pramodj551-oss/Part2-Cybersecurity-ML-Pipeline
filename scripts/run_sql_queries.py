"""Execute and audit the 29 SQL analytics queries from Part 1 against Part 2 data.

Only legitimate compatibility fields are derived from incident_date:
incident_year, incident_month and is_weekend. Unsupported Part 1 fields are
reported as BLOCKED rather than fabricated.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "raw" / "cybersecurity_incident_reports.csv"
SQL_FILE = ROOT / "queries.sql"
OUTPUT = ROOT / "outputs"

RAW_COLUMNS = {
    "incident_id", "incident_date", "sector", "region", "attack_type",
    "threat_actor", "records_affected", "downtime_hours", "ransom_demand_usd",
    "detection_time_hours", "severity_score", "response_team_size",
    "regulatory_fine_usd", "resolved_within_7_days", "data_exfiltration",
    "zero_day_used",
}

# These fields do not exist in Part 2 and are intentionally NOT fabricated.
BLOCKED_FIELDS = {"total_financial_impact", "risk_score", "incident_complexity_score"}


def load_queries(text: str) -> dict[int, str]:
    parts = re.split(r"(?m)^--\s*(\d+)\.\s+", text)
    queries: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        body = parts[i + 1]
        # Strip divider/comments and keep the SQL statement.
        statements = [
            line for line in body.splitlines()
            if not line.strip().startswith("--") and line.strip()
        ]
        sql = "\n".join(statements).strip()
        if sql:
            queries[number] = sql
    return queries


def main() -> int:
    if not DATASET.exists():
        raise FileNotFoundError(DATASET)
    if not SQL_FILE.exists():
        raise FileNotFoundError(SQL_FILE)

    df = pd.read_csv(DATASET)
    missing = RAW_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset schema missing columns: {sorted(missing)}")

    # Legitimate date-derived compatibility fields only.
    dates = pd.to_datetime(df["incident_date"], errors="coerce")
    df = df.copy()
    df["incident_year"] = dates.dt.year
    df["incident_month"] = dates.dt.month
    df["is_weekend"] = dates.dt.dayofweek.isin([5, 6]).astype(int)

    queries = load_queries(SQL_FILE.read_text(encoding="utf-8"))
    if set(queries) != set(range(1, 30)):
        raise ValueError(f"Expected exactly 29 queries; found {sorted(queries)}")

    conn = sqlite3.connect(":memory:")
    try:
        df.to_sql("cybersecurity_incidents", conn, index=False, if_exists="replace")
        rows = []
        for number in range(1, 30):
            sql = queries[number]
            referenced_blocked = sorted(
                field for field in BLOCKED_FIELDS
                if re.search(rf"\b{re.escape(field)}\b", sql, flags=re.I)
            )
            if referenced_blocked:
                rows.append({
                    "query_id": number,
                    "status": "BLOCKED",
                    "reason": f"Unsupported Part 2 field(s): {', '.join(referenced_blocked)}",
                    "row_count": None,
                })
                continue
            try:
                result = pd.read_sql_query(sql, conn)
                rows.append({
                    "query_id": number,
                    "status": "PASS",
                    "reason": "Executed successfully",
                    "row_count": int(len(result)),
                })
            except Exception as exc:
                rows.append({
                    "query_id": number,
                    "status": "FAIL",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "row_count": None,
                })
    finally:
        conn.close()

    report = pd.DataFrame(rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT / "sql_query_validation.csv", index=False)
    summary = {
        "total_queries": 29,
        "pass": int((report.status == "PASS").sum()),
        "fail": int((report.status == "FAIL").sum()),
        "blocked": int((report.status == "BLOCKED").sum()),
        "derived_compatibility_fields": ["incident_year", "incident_month", "is_weekend"],
        "blocked_fields": sorted(BLOCKED_FIELDS),
        "dataset_rows": int(len(df)),
    }
    (OUTPUT / "sql_query_validation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    # BLOCKED is an audited/expected state; only unexpected SQL failures fail CI.
    return 1 if summary["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
