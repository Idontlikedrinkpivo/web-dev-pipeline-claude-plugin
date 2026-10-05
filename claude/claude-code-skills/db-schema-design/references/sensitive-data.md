# Sensitive data (PII, secrets)

Read when the SRS flags a column as PII, a credential, or a secret. Do not
invent classification the SRS never stated.

| Data kind | Pattern |
|---|---|
| PII shown back to its owner only (email, phone, address) | Plain column. Who may read it is decided later, in architecture, not by the column type. No column-level encryption by default. |
| PII the SRS says must be unreadable even via direct DB access (SSN, government ID, payment-adjacent fields) | `bytea` column + `pgcrypto` (`pgp_sym_encrypt`/`pgp_sym_decrypt`) or application-layer encryption before the value reaches SQL. If the SRS requires unreadability and does not say which, ask once. Do not encrypt a column the SRS does not call out. |
| Credentials / tokens / API keys | **Never store in plaintext.** Passwords: salted hash (bcrypt/argon2) in the app layer, column is just `text` for the hash. Long-lived tokens/API keys: store a hash or a truncated lookup prefix + hash, never the raw secret |
| Data with a stated retention limit | A `deleted_at`/`purge_after` column plus a documented job that enforces it — this skill defines the column, not the job |

```sql
-- ✅ hash, never the raw secret
CREATE TABLE api_keys (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    key_hash    text NOT NULL UNIQUE,       -- sha256/bcrypt of the raw key
    key_prefix  text NOT NULL,              -- short, non-secret, for display/lookup
    user_id     bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at  timestamptz NOT NULL DEFAULT now(),
    revoked_at  timestamptz
);

-- ❌ never
CREATE TABLE api_keys (id bigint GENERATED ALWAYS AS IDENTITY, raw_key text, ...);
```

Do not add row-level encryption, masking views, or audit-log tables the
SRS didn't ask for — that is scope creep on a greenfield schema, same
discipline as not adding multi-tenancy the SRS never named.
