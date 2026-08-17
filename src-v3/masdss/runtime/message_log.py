"""WP0 / T6.1 — Nhat ky message: NGUON SU THAT duy nhat.

Phuc vu: RQ2 (truy vet duoc), RQ1 (dung lai chuyen gi da xay ra khi tiem loi).

Day khong phai log phu tro. RQ2 do tren no, va DP4 buoc decision trace chi duoc
dung tu no. Vi vay no la san pham hang nhat: co schema, co test, append-only.

APPEND-ONLY duoc cuong che o hai tang:
  - Lop nay khong co bat ky phuong thuc update/delete nao.
  - Trigger SQLite chan lenh UPDATE va DELETE tu moi duong khac.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

from masdss.core.message import Message

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    rowid_          INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id          TEXT NOT NULL UNIQUE,
    conversation_id TEXT NOT NULL,
    trace_id        TEXT NOT NULL,
    in_reply_to     TEXT,
    sender          TEXT NOT NULL,
    receiver        TEXT NOT NULL,
    performative    TEXT NOT NULL,
    ontology        TEXT NOT NULL,
    content_json    TEXT NOT NULL,
    seq             INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conv ON messages(conversation_id, seq, rowid_);

CREATE TRIGGER IF NOT EXISTS messages_no_update
BEFORE UPDATE ON messages
BEGIN
    SELECT RAISE(ABORT, 'nhat ky message la append-only');
END;

CREATE TRIGGER IF NOT EXISTS messages_no_delete
BEFORE DELETE ON messages
BEGIN
    SELECT RAISE(ABORT, 'nhat ky message la append-only');
END;
"""

_COLUMNS = (
    "msg_id", "conversation_id", "trace_id", "in_reply_to",
    "sender", "receiver", "performative", "ontology", "content_json", "seq",
)


class MessageLog:
    """Nhat ky ben vung tren SQLite. Mot tep, khong dich vu nen."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def append(self, message: Message) -> None:
        row = message.to_row()
        placeholders = ", ".join("?" for _ in _COLUMNS)
        self._conn.execute(
            f"INSERT INTO messages ({', '.join(_COLUMNS)}) VALUES ({placeholders})",
            tuple(row[c] for c in _COLUMNS),
        )
        self._conn.commit()

    def conversation(self, conversation_id: UUID | str) -> list[Message]:
        """Moi message cua mot case, theo dung thu tu da ghi."""
        cursor = self._conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY seq, rowid_",
            (str(conversation_id),),
        )
        return [Message.from_row(dict(row)) for row in cursor.fetchall()]

    def conversation_ids(self) -> list[str]:
        cursor = self._conn.execute(
            "SELECT DISTINCT conversation_id FROM messages ORDER BY conversation_id"
        )
        return [row[0] for row in cursor.fetchall()]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0])

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "MessageLog":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
