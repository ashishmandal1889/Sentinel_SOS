"""
Sentinel SOS - MongoDB Connection & Index Diagnostic Script.

Run this script to test connectivity to your MongoDB cluster and verify
index initialization:
    python test_mongo_connection.py
"""

import sys
from app.core.config import settings
from app.db.mongodb import mongo_manager, check_mongo_connection, init_mongo_indexes

def main():
    print("=" * 60)
    print("Sentinel SOS - MongoDB Connectivity Diagnostic")
    print("=" * 60)
    print(f"Target Database : {settings.MONGO_DATABASE}")
    
    # Mask password in URI for safe display
    uri_display = settings.MONGO_URI
    if "@" in uri_display and "://" in uri_display:
        prefix, rest = uri_display.split("://", 1)
        user_pass, host = rest.split("@", 1)
        username = user_pass.split(":", 1)[0]
        uri_display = f"{prefix}://{username}:****@{host}"
    print(f"Connection URI  : {uri_display}")
    print("-" * 60)

    if "<db_password>" in settings.MONGO_URI:
        print("[!] ERROR: '<db_password>' placeholder detected in MONGO_URI.")
        print("    Please replace '<db_password>' with your actual database user password in backend/.env.")
        sys.exit(1)

    print("[*] Testing MongoDB connection ping...")
    is_connected = check_mongo_connection()

    if is_connected:
        print("[+] SUCCESS: Successfully connected to MongoDB!")
        print("[*] Initializing collections and indexes...")
        indexes_ok = init_mongo_indexes()
        if indexes_ok:
            print("[+] SUCCESS: Indexes verified and initialized for:")
            print("    - sos_incidents (incident_id, citizen_id+created_at, status, coordinates)")
            print("    - sos_events (incident_id+timestamp, event_id)")
            print("    - responder_location_history (responder_id+timestamp)")
            print("    - notification_attempts (incident_id+created_at, attempt_id)")
            print("    - incident_snapshots (incident_id+snapshot_at)")
        else:
            print("[-] Warning: Failed to initialize one or more indexes.")
    else:
        print("[-] FAILED: Could not establish connection to MongoDB cluster.")
        print("    Common causes:")
        print("    1. Incorrect database user password in .env")
        print("    2. IP Access List on MongoDB Atlas (whitelist your current IP or allow 0.0.0.0/0)")
        print("    3. Network firewall blocking outbound port 27017")
    print("=" * 60)

if __name__ == "__main__":
    main()
