"""
InsightFlow – SQLite Database Manager
Handles persistence for datasets, dashboards, and chart configurations.
"""

import sqlite3
import json
import os
from datetime import datetime
from config import DB_PATH


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            row_count INTEGER DEFAULT 0,
            col_count INTEGER DEFAULT 0,
            columns_json TEXT DEFAULT '[]',
            file_size_bytes INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            dataset_id INTEGER,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dashboard_id INTEGER NOT NULL,
            chart_type TEXT NOT NULL,
            title TEXT DEFAULT 'Untitled Chart',
            config_json TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (dashboard_id) REFERENCES dashboards(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()


# ──────────────────────── Dataset Operations ──────────────────────────

def save_dataset(name, filename, row_count, col_count, columns, file_size_bytes=0):
    """Save dataset metadata to DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO datasets (name, filename, uploaded_at, row_count, col_count, columns_json, file_size_bytes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, filename, datetime.now().isoformat(), row_count, col_count,
         json.dumps(columns), file_size_bytes)
    )
    dataset_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dataset_id


def get_all_datasets():
    """Get all datasets."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM datasets ORDER BY uploaded_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_dataset(dataset_id):
    """Delete a dataset by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
    conn.commit()
    conn.close()


# ──────────────────────── Dashboard Operations ────────────────────────

def save_dashboard(name, description="", dataset_id=None):
    """Create a new dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """INSERT INTO dashboards (name, description, created_at, updated_at, dataset_id)
           VALUES (?, ?, ?, ?, ?)""",
        (name, description, now, now, dataset_id)
    )
    dashboard_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dashboard_id


def get_all_dashboards():
    """Get all dashboards."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM dashboards ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard(dashboard_id):
    """Get a single dashboard by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM dashboards WHERE id = ?", (dashboard_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_dashboard(dashboard_id, name=None, description=None):
    """Update dashboard details."""
    conn = get_connection()
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(dashboard_id)
    conn.execute(f"UPDATE dashboards SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()


def delete_dashboard(dashboard_id):
    """Delete a dashboard and its charts."""
    conn = get_connection()
    conn.execute("DELETE FROM charts WHERE dashboard_id = ?", (dashboard_id,))
    conn.execute("DELETE FROM dashboards WHERE id = ?", (dashboard_id,))
    conn.commit()
    conn.close()


# ──────────────────────── Chart Operations ────────────────────────────

def save_chart(dashboard_id, chart_type, title, config, position=0):
    """Save a chart to a dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO charts (dashboard_id, chart_type, title, config_json, position, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (dashboard_id, chart_type, title, json.dumps(config),
         position, datetime.now().isoformat())
    )
    chart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chart_id


def get_charts_for_dashboard(dashboard_id):
    """Get all charts for a dashboard."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM charts WHERE dashboard_id = ? ORDER BY position",
        (dashboard_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_chart(chart_id):
    """Delete a chart by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM charts WHERE id = ?", (chart_id,))
    conn.commit()
    conn.close()


# ──────────────────────── User Operations ───────────────────────────────

def create_user(username, password_hash):
    """Create a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, datetime.now().isoformat())
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Username already exists
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieve a user by username."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None
