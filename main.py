from fastapi import FastAPI, Request, Query
import json
import tarfile
import sqlite3
import io
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import logging

# Set up logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def init_db():
    conn = sqlite3.connect("huginn.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,              -- UUID from Muninn
        content TEXT NOT NULL,            -- Note text
        created_at TIMESTAMP,             -- Original timestamp from Muninn
        updated_at TIMESTAMP,             -- Last update time
        content_hash TEXT,                -- Hash for change detection
        summary TEXT,                     -- LLM-generated summary
        tags TEXT                         -- Tags (manual or auto)
    )
    """)

    # Attachments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id TEXT NOT NULL,            -- FK to notes.id
        file_name TEXT NOT NULL,          -- Original filename
        file_type TEXT,                   -- MIME type
        file_path TEXT NOT NULL,          -- Path on disk
        FOREIGN KEY(note_id) REFERENCES notes(id)
            ON DELETE CASCADE,            -- If note is deleted, delete attachments
        UNIQUE(note_id, file_name, file_path) -- Prevent duplicate attachments
    )
    """)

    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts
    USING fts5(content, content='notes', content_rowid='rowid');
    """)

    # keep fts in sync
    cursor.executescript("""
    CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
        INSERT INTO notes_fts(rowid, content) VALUES (new.rowid, new.content);
    END;

    CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
        INSERT INTO notes_fts(notes_fts, rowid, content) VALUES('delete', old.rowid, old.content);
    END;

    CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
        INSERT INTO notes_fts(notes_fts, rowid, content) VALUES('delete', old.rowid, old.content);
        INSERT INTO notes_fts(rowid, content) VALUES (new.rowid, new.content);
    END;
    """)
    conn.commit()
    return conn


conn = init_db()

@app.post("/upload")
async def upload_file(request: Request):
    body = await request.body()
    file_like = io.BytesIO(body)

    date_str = datetime.now().strftime("%Y-%m-%d")
    extract_path = os.path.join("uploads", date_str)
    os.makedirs(extract_path, exist_ok=True)

    notes_json_path = None

    with tarfile.open(fileobj=file_like, mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                tar.extract(member, path=extract_path)
                if member.name.endswith(".json"):
                    notes_json_path = os.path.join(extract_path, member.name)

    if not notes_json_path:
        return {"status": "error", "message": "No notes.json found"}

    with open(notes_json_path, "r", encoding="utf-8") as f:
        notes = json.load(f)

    for note in notes:
        note_id = note["id"]
        text = note.get("text", "")
        timestamp = note.get("timestamp")

        conn.execute(
            "INSERT OR REPLACE INTO notes (id, content, created_at) VALUES (?, ?, ?)",
            (note_id, text, timestamp)
        )

        for att in note.get("attachments", []):
            file_name = att.get("fileName")
            file_type = att.get("fileType")
            file_path = os.path.join(extract_path, att.get("filePath"))

            conn.execute(
                "INSERT INTO attachments (note_id, file_name, file_type, file_path) VALUES (?, ?, ?, ?)",
                (note_id, file_name, file_type, file_path)
            )

    conn.commit()
    return {"status": "ok", "notes_inserted": len(notes)}

@app.get("/search")
async def search_notes(q: str = Query(..., description="Search query")):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.id, n.content, n.created_at, n.updated_at
        FROM notes_fts f
        JOIN notes n ON n.rowid = f.rowid
        WHERE notes_fts MATCH ?
        ORDER BY rank
        LIMIT 20
    """, (q,))
    results = cursor.fetchall()

    return [
        {
            "id": r[0],
            "content": r[1],
            "created_at": r[2],
            "updated_at": r[3]
        }
        for r in results
    ]
def main():
    print("Running")
