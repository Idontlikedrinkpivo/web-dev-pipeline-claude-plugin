# Situational schema patterns

Read when the SRS asks for one of these. Do not add any of them by
default: each is extra state every query must account for.

## Soft delete (only if the SRS calls for it)

```sql
ALTER TABLE orders ADD COLUMN deleted_at timestamptz;
CREATE INDEX idx_orders_active ON orders(status, created_at DESC) WHERE deleted_at IS NULL;
```

The partial index keeps the hot "active rows" query fast without indexing
deleted rows nobody reads.

## Avoid polymorphic foreign keys

A `(type, id)` pair cannot be a `FOREIGN KEY`, so nothing stops it from
pointing at a row that does not exist.

```sql
-- ❌ no referential integrity possible
CREATE TABLE comments (id bigint GENERATED ALWAYS AS IDENTITY, commentable_type text, commentable_id bigint);

-- ✅ separate nullable FK columns with a CHECK, or separate tables entirely
CREATE TABLE comments (
    id       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    post_id  bigint REFERENCES posts(id) ON DELETE CASCADE,
    photo_id bigint REFERENCES photos(id) ON DELETE CASCADE,
    CHECK ((post_id IS NOT NULL) <> (photo_id IS NOT NULL))
);
```

## JSONB — only for genuinely flexible data

```sql
attributes jsonb NOT NULL DEFAULT '{}'   -- ✅ optional, schema-less metadata
```

Never use JSONB for a field the SRS names (email, status, price) — those
are columns.
