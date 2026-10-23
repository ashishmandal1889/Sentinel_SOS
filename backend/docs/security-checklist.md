# Security checklist

- Verify Firebase ID tokens on protected routes.
- Enforce role permissions on the server, not just in the UI.
- Restrict access to each user's contacts and incident data.
- Keep API keys out of Git and frontend bundles; restrict browser keys by referrer/API.
- Add rate limits, idempotency, audit logs, and monitoring.
- Minimize location retention and document consent/deletion policy.
- Test notification provider outages and escalation paths.
- Do not claim police/ambulance dispatch without an authorized integration and confirmation.
- FCM must not be the sole channel for life-critical alerts.
