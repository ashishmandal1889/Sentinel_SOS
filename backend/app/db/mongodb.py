"""
Sentinel SOS - Document Database Connection (MongoDB).

Manages PyMongo client, collection handles, index initialization, and connection health diagnostics.
Collections:
  - sos_incidents
  - sos_events
  - responder_location_history
  - notification_attempts
  - incident_snapshots
"""

from typing import Optional
from app.core.config import settings
from app.core.logging import logger

try:
    from pymongo import ASCENDING, DESCENDING, MongoClient
    from pymongo.database import Database
except ImportError:
    MongoClient = None
    Database = None
    ASCENDING = 1
    DESCENDING = -1


class MongoManager:
    """Singleton connection manager for MongoDB."""
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None

    def get_client(self) -> Optional[MongoClient]:
        if MongoClient is None:
            logger.warning("PyMongo library is not installed.")
            return None

        if self._client is None:
            # Don't attempt connection if URI still contains unconfigured placeholder
            if "<db_password>" in settings.MONGO_URI:
                logger.warning("MongoDB URI contains '<db_password>' placeholder. Please provide the actual password in .env.")
                return None

            try:
                self._client = MongoClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                )
            except Exception as e:
                logger.error(f"Failed to initialize MongoClient: {e}")
                return None
        return self._client

    def get_database(self) -> Optional[Database]:
        client = self.get_client()
        if client is not None:
            return client[settings.MONGO_DATABASE]
        return None

    def check_connection(self) -> bool:
        """Pings MongoDB to verify connectivity."""
        try:
            client = self.get_client()
            if client is None:
                return False
            client.admin.command("ping")
            return True
        except Exception as e:
            logger.warning(f"MongoDB connection ping failed: {e}")
            return False

    def init_indexes(self) -> bool:
        """Initializes collections and indexes on MongoDB."""
        db = self.get_database()
        if db is None:
            return False

        try:
            # 1. sos_incidents
            incidents = db["sos_incidents"]
            incidents.create_index([("incident_id", ASCENDING)], unique=True)
            incidents.create_index([("citizen_id", ASCENDING), ("created_at", DESCENDING)])
            incidents.create_index([("status", ASCENDING)])
            incidents.create_index([("latitude", ASCENDING), ("longitude", ASCENDING)])

            # 2. sos_events
            events = db["sos_events"]
            events.create_index([("incident_id", ASCENDING), ("timestamp", ASCENDING)])
            events.create_index([("event_id", ASCENDING)], unique=True)

            # 3. responder_location_history
            loc_history = db["responder_location_history"]
            loc_history.create_index([("responder_id", ASCENDING), ("timestamp", DESCENDING)])

            # 4. notification_attempts
            notifs = db["notification_attempts"]
            notifs.create_index([("incident_id", ASCENDING), ("created_at", DESCENDING)])
            notifs.create_index([("attempt_id", ASCENDING)], unique=True)

            # 5. incident_snapshots
            snapshots = db["incident_snapshots"]
            snapshots.create_index([("incident_id", ASCENDING), ("snapshot_at", DESCENDING)])

            logger.info("MongoDB collections and indexes verified/created successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
            return False

    def close(self):
        if self._client:
            self._client.close()
            self._client = None


mongo_manager = MongoManager()


def get_mongo_db() -> Optional[Database]:
    """Dependency / accessor for MongoDB database instance."""
    return mongo_manager.get_database()


def check_mongo_connection() -> bool:
    """Verifies MongoDB connectivity."""
    return mongo_manager.check_connection()


def init_mongo_indexes() -> bool:
    """Ensures indexes are created on MongoDB."""
    return mongo_manager.init_indexes()
