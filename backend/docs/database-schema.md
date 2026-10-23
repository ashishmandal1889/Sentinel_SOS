# Sentinel SOS — Database Schema Documentation

## 1. Relational Database (PostgreSQL)

### `roles`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string |
| `name` | VARCHAR(50) | UNIQUE, NOT NULL | Role name (`citizen`, `responder`, `admin`) |
| `description` | VARCHAR(255) | NULLABLE | Role description |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Update timestamp |

### `users`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Account email |
| `full_name` | VARCHAR(255) | NOT NULL | User's full name |
| `phone_number` | VARCHAR(32) | UNIQUE, NOT NULL | Primary contact phone |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hash |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active flag |
| `role_id` | VARCHAR(36) | FOREIGN KEY (`roles.id`) | Assigned role |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Update timestamp |

### `responders`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string |
| `user_id` | VARCHAR(36) | FOREIGN KEY (`users.id`), UNIQUE | Linked user account |
| `badge_number` | VARCHAR(64) | UNIQUE | Responder badge ID |
| `status` | VARCHAR(32) | DEFAULT 'OFFLINE' | Status (`AVAILABLE`, `BUSY`, `OFFLINE`) |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Administrator verification |
| `service_radius_km`| FLOAT | DEFAULT 15.0 | Max service dispatch radius |
| `current_latitude` | FLOAT | NULLABLE | Last reported latitude |
| `current_longitude`| FLOAT | NULLABLE | Last reported longitude |
| `location_updated_at`| TIMESTAMP WITH TIME ZONE | NULLABLE | Timestamp of last location update |
| `qualifications` | VARCHAR(255) | DEFAULT 'GENERAL' | Emergency specialties (e.g. `MEDICAL,FIRE`) |

### `emergency_contacts`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string |
| `user_id` | VARCHAR(36) | FOREIGN KEY (`users.id`) | Citizen owner |
| `contact_name` | VARCHAR(255) | NOT NULL | Contact name |
| `relationship_label`| VARCHAR(64) | NOT NULL | Relationship (Parent, Spouse, etc.) |
| `phone_number` | VARCHAR(32) | NOT NULL | Phone number for alerts |
| `email` | VARCHAR(255) | NULLABLE | Email for notification |
| `priority_order` | INTEGER | DEFAULT 1 | Alert order priority |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status |

### `incident_assignments`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | UUID string |
| `incident_id` | VARCHAR(64) | NOT NULL, INDEX | Foreign key to MongoDB incident |
| `responder_id` | VARCHAR(36) | FOREIGN KEY (`responders.id`) | Assigned responder |
| `status` | VARCHAR(32) | DEFAULT 'OFFERED' | Status (`OFFERED`, `ACCEPTED`, `DECLINED`) |
| `offered_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | Dispatch offer timestamp |
| `responded_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Acceptance timestamp |
| `arrived_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | On-scene arrival timestamp |
| `completed_at` | TIMESTAMP WITH TIME ZONE | NULLABLE | Resolution timestamp |
| `eta_seconds` | INTEGER | NULLABLE | Route calculated ETA |
| `distance_meters`| FLOAT | NULLABLE | Driving distance |

---

## 2. Document Store (MongoDB)

### Collection: `sos_incidents`
```json
{
  "incident_id": "inc_a8f9c102b4d1",
  "citizen_id": "060d5b4a-b5e1-4c17-91a1-3fc5e8e89fbc",
  "emergency_type": "MEDICAL",
  "status": "CREATED",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy_meters": 4.5,
  "description": "Shortness of breath.",
  "metadata": {},
  "created_at": "ISODate()",
  "updated_at": "ISODate()"
}
```
**Indexes**:
- `{"incident_id": 1}` (Unique)
- `{"citizen_id": 1, "created_at": -1}`
- `{"status": 1}`
- `{"latitude": 1, "longitude": 1}` (2dsphere index for spatial queries)

### Collection: `sos_events`
```json
{
  "event_id": "evt_91b72e40aa",
  "incident_id": "inc_a8f9c102b4d1",
  "event_type": "STATUS_CHANGED",
  "from_status": "CREATED",
  "to_status": "NOTIFYING",
  "note": "SMS notifications dispatched to 2 emergency contacts.",
  "timestamp": "ISODate()"
}
```
**Indexes**:
- `{"incident_id": 1, "timestamp": 1}`
- `{"event_type": 1}`
