"""Single audited report-write implementation shared by UI and agent tool."""
from pathlib import Path
import json
import re
from datetime import datetime, timezone


def save_approved_report(alert_id: str, summary: str, reports_dir: Path, *, approved: bool) -> dict:
    """Save only a verified human-approved draft; never take directions from alert notes."""
    if not approved:
        return {"saved": False, "reason": "human_approval_required"}
    alert_id = alert_id.strip().upper()
    if not re.fullmatch(r"FR[0-9]{3}", alert_id):
        return {"saved": False, "reason": "invalid_alert_id"}
    if not isinstance(summary, str) or not summary.strip():
        return {"saved": False, "reason": "empty_summary"}
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{alert_id}.txt"
    path.write_text(summary.strip()[:8000] + "\n", encoding="utf-8")
    audit = reports_dir.parent / "report_approvals.jsonl"
    with audit.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp_utc":datetime.now(timezone.utc).isoformat(),"event":"human_approved_report_save","alert_id":alert_id,"saved":True,"file":str(path.name)}, ensure_ascii=False) + "\n")
    return {"saved": True, "alert_id": alert_id, "path": str(path), "bytes": path.stat().st_size}

# Local, persistent archive accessible from the web dashboard.
import sqlite3


def _connect_archive(db_path: Path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=15)
    conn.execute('''CREATE TABLE IF NOT EXISTS approved_reports (
        alert_id TEXT PRIMARY KEY,
        body TEXT NOT NULL,
        approved_at_utc TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'مسودة معتمدة للحفظ'
    )''')
    return conn


def save_to_archive(alert_id: str, body: str, db_path: Path, *, approved: bool) -> dict:
    """Persist only an approved report. No model-authored approval is accepted."""
    if not approved:
        return {'saved': False, 'reason': 'human_approval_required'}
    alert_id = str(alert_id).strip().upper()
    if not re.fullmatch(r'FR[0-9]{3}', alert_id):
        return {'saved': False, 'reason': 'invalid_alert_id'}
    if not isinstance(body, str) or not body.strip():
        return {'saved': False, 'reason': 'empty_report'}
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with _connect_archive(db_path) as con:
        con.execute('''INSERT INTO approved_reports (alert_id, body, approved_at_utc)
            VALUES (?, ?, ?)
            ON CONFLICT(alert_id) DO UPDATE SET
            body=excluded.body, approved_at_utc=excluded.approved_at_utc''',
            (alert_id, body.strip()[:12000], timestamp))
    return {'saved': True, 'alert_id': alert_id, 'timestamp': timestamp}


def list_archive(db_path: Path) -> list[dict]:
    with _connect_archive(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute('''SELECT alert_id, body, approved_at_utc, status
                              FROM approved_reports ORDER BY approved_at_utc DESC''').fetchall()
    return [dict(row) for row in rows]
