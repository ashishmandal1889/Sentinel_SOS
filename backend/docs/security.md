# Sentinel SOS — Security Policy & Checklist

## 1. Security Architecture Principles

### Zero-Trust User Identity
- **Never trust user IDs from request bodies**: User identities are extracted exclusively from cryptographically verified JWT Bearer tokens via FastAPI dependency `get_current_user`.
- **Ownership Verification**: Endpoints managing emergency contacts and viewing incident details verify that the caller either owns the resource or has an authorized `admin` role.

### Secret & Key Management
1. **Never Hardcode Secrets**: All API keys, credentials, and secrets are read from the environment via Pydantic Settings (`app/core/config.py`).
2. **Secret Masking**: Configuration validators produce clear human-readable error messages without leaking secret values or token prefixes.
3. **Repository Cleanliness**: `.env`, `.env.*.local`, `service-account*.json`, and private keys are barred by `.gitignore`.
4. **Production Hardening**: Production mode refuses insecure fallback keys or SQLite databases, failing fast during startup if requirements are not met.

### Password Security & Hashing
- Passwords are encrypted using modern `bcrypt` salt generation before SQL storage.
- Passwords are never returned in responses or serialized in logs.
- Plaintext inputs longer than 72 bytes are safely truncated to protect against algorithm buffer overruns.

### Input Validation & Defensive Ingestion
- Geographic coordinates are validated using strict spherical constraints ($-90.0 \le \text{lat} \le 90.0$, $-180.0 \le \text{lon} \le 180.0$).
- Request payloads enforce string length boundaries and data types via Pydantic V2 models.
- Idempotency keys (`client_request_id`) prevent duplicate emergency incidents caused by unstable mobile connectivity or rapid repeated citizen taps.

## 2. Pre-Deployment Security Checklist

- [ ] `SENTINEL_ENV` set to `production`.
- [ ] `AUTH_SECRET_KEY` replaced with a high-entropy cryptographically generated 256-bit secret.
- [ ] `SQL_DATABASE_URL` configured to a secured, TLS-encrypted PostgreSQL instance.
- [ ] Google Maps API key restricted in Google Cloud Console by IP/service account to Directions and Geocoding APIs only.
- [ ] Twilio / MSG91 credentials scoped strictly to messaging services.
- [ ] CORS origins (`SENTINEL_ALLOWED_ORIGINS`) narrowed to legitimate frontend domains.
- [ ] Reverse proxy (e.g. Nginx, Cloudflare, AWS ALB) configured for HTTPS termination and rate limiting.
