import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from contextlib import contextmanager

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "trips.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Initializes database tables and safely performs non-destructive migrations.
    Preserves all existing data.
    """
    with get_connection() as conn:
        # 1. Users Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 2. Trips Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                destination TEXT NOT NULL,
                origin TEXT,
                duration_days INTEGER NOT NULL,
                dates TEXT,
                travelers_count INTEGER NOT NULL,
                traveler_type TEXT,
                currency TEXT NOT NULL,
                total_budget REAL,
                estimated_cost REAL,
                vibe_summary TEXT,
                user_id TEXT,
                full_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 3. Check for missing columns in existing trips table (Migration)
        cursor = conn.execute("PRAGMA table_info(trips)")
        existing_columns = [row["name"] for row in cursor.fetchall()]

        if "user_id" not in existing_columns:
            conn.execute("ALTER TABLE trips ADD COLUMN user_id TEXT")
        if "quality_score" not in existing_columns:
            conn.execute("ALTER TABLE trips ADD COLUMN quality_score REAL")
        if "cost_before_optimization" not in existing_columns:
            conn.execute("ALTER TABLE trips ADD COLUMN cost_before_optimization REAL")
        if "cost_after_optimization" not in existing_columns:
            conn.execute("ALTER TABLE trips ADD COLUMN cost_after_optimization REAL")
        if "is_optimized" not in existing_columns:
            conn.execute("ALTER TABLE trips ADD COLUMN is_optimized INTEGER DEFAULT 0")

        # 4. Indices for fast querying and isolation
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trips_user_id ON trips(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.commit()


# ============================================================================
# USER OPERATIONS
# ============================================================================

def create_user(full_name: str, email: str, password_hash: str) -> Dict[str, Any]:
    """
    Creates a new user record with a normalized email and unique ID.
    """
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()
    clean_email = email.strip().lower()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (id, full_name, email, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, full_name.strip(), clean_email, password_hash, now, now))
        conn.commit()

    return {
        "id": user_id,
        "full_name": full_name.strip(),
        "email": clean_email,
        "created_at": now,
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Finds a user by normalized email address.
    """
    clean_email = email.strip().lower()
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, full_name, email, password_hash, created_at, updated_at
            FROM users
            WHERE email = ?
        """, (clean_email,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Finds a user by unique user ID.
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, full_name, email, created_at, updated_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


# ============================================================================
# TRIP OPERATIONS
# ============================================================================

def save_trip(trip_dict: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Saves the COMPLETE generated itinerary, all day-wise activities,
    budget details, map coordinates, checklist, and metadata to SQLite.
    Associates the trip with user_id if provided.
    """
    trip_id = trip_dict.get("trip_id")
    if not trip_id:
        trip_id = f"trip_{uuid.uuid4().hex[:8]}"
        trip_dict["trip_id"] = trip_id

    # Associate ownership
    effective_user_id = user_id or trip_dict.get("user_id")
    if effective_user_id:
        trip_dict["user_id"] = effective_user_id
    else:
        trip_dict["user_id"] = None

    # Summary fields for indexing and quick listing
    title = trip_dict.get("title", f"Trip to {trip_dict.get('destination', 'Destination')}")
    destination = trip_dict.get("destination", "")
    origin = trip_dict.get("origin", "")
    duration_days = int(trip_dict.get("duration_days", 5))
    dates = trip_dict.get("dates", f"{duration_days} Days Exploration")
    travelers_count = int(trip_dict.get("travelers_count", 2))
    traveler_type = trip_dict.get("traveler_type", "Travelers")
    currency = trip_dict.get("currency", "USD")

    # Financial summary extraction
    budget = trip_dict.get("budget_breakdown", {})
    total_budget = float(
        budget.get("total_budget")
        or trip_dict.get("budget_total")
        or trip_dict.get("total_budget")
        or 0.0
    )
    estimated_cost = float(
        budget.get("estimated_total_cost")
        or trip_dict.get("estimated_cost")
        or 0.0
    )
    vibe_summary = trip_dict.get("vibe_summary", "")

    now = datetime.now().isoformat()
    if "created_at" not in trip_dict:
        trip_dict["created_at"] = now
    trip_dict["updated_at"] = now

    # Remove any private secrets before serialization
    safe_data = {k: v for k, v in trip_dict.items() if k not in ("api_key", "password", "password_hash")}
    full_data_json = json.dumps(safe_data, ensure_ascii=False)

    quality_score = float(trip_dict.get("quality_score") or 0.0)
    cost_before = float(trip_dict.get("cost_before_optimization") or trip_dict.get("original_estimated_cost") or estimated_cost)
    cost_after = float(trip_dict.get("cost_after_optimization") or estimated_cost)
    is_opt = 1 if trip_dict.get("is_optimized") else 0

    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO trips (
                id, title, destination, origin, duration_days, dates,
                travelers_count, traveler_type, currency, total_budget,
                estimated_cost, vibe_summary, user_id, full_data,
                quality_score, cost_before_optimization, cost_after_optimization, is_optimized,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trip_id, title, destination, origin, duration_days, dates,
            travelers_count, traveler_type, currency, total_budget,
            estimated_cost, vibe_summary, trip_dict["user_id"], full_data_json,
            quality_score, cost_before, cost_after, is_opt,
            trip_dict["created_at"], now
        ))
        conn.commit()

    return trip_dict


def get_trip(trip_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves the complete stored itinerary by trip ID.
    Enforces user isolation:
    - If the trip belongs to a user, only that user can access it.
    - If the trip is a guest/legacy trip (user_id IS NULL), it can be retrieved.
    - If another user tries to fetch a private trip, returns None.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT full_data, user_id FROM trips WHERE id = ?",
            (trip_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        trip_owner = row["user_id"]

        # Enforce user isolation:
        # If the trip is owned by a specific user, check that user_id matches
        if trip_owner is not None:
            if user_id is None or user_id != trip_owner:
                return None

        return json.loads(row["full_data"])


def list_trips(user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Returns saved trip summaries.
    - If user_id is provided, returns ONLY trips owned by that user.
    - If user_id is None, returns guest trips (user_id IS NULL).
    """
    with get_connection() as conn:
        if user_id is not None:
            cursor = conn.execute("""
                SELECT id, title, destination, origin, duration_days, dates,
                       travelers_count, traveler_type, currency, total_budget,
                       estimated_cost, vibe_summary, user_id,
                       quality_score, cost_before_optimization, cost_after_optimization, is_optimized,
                       created_at
                FROM trips
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor = conn.execute("""
                SELECT id, title, destination, origin, duration_days, dates,
                       travelers_count, traveler_type, currency, total_budget,
                       estimated_cost, vibe_summary, user_id,
                       quality_score, cost_before_optimization, cost_after_optimization, is_optimized,
                       created_at
                FROM trips
                WHERE user_id IS NULL
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_trip(trip_id: str, user_id: Optional[str] = None) -> bool:
    """
    Deletes a saved trip from SQLite.
    Verifies that the user owns the trip (or it's a guest trip if user_id is None).
    """
    with get_connection() as conn:
        if user_id is not None:
            cursor = conn.execute(
                "DELETE FROM trips WHERE id = ? AND user_id = ?",
                (trip_id, user_id)
            )
        else:
            cursor = conn.execute(
                "DELETE FROM trips WHERE id = ? AND user_id IS NULL",
                (trip_id,)
            )

        conn.commit()
        return cursor.rowcount > 0


# Initialize tables and migrations immediately on import
init_db()
