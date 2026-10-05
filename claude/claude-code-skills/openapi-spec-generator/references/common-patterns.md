# Common OpenAPI Patterns

## Contents

- [Pagination](#pagination)
- [Problem Details (RFC 9457, obsoletes RFC 7807)](#problem-details-rfc-9457-obsoletes-rfc-7807)
- [File Upload](#file-upload)
- [Callbacks](#callbacks)
- [HATEOAS Links](#hateoas-links)
- [Sorting and Filtering](#sorting-and-filtering)
- [Versioning Patterns](#versioning-patterns)
- [Rate Limiting Headers](#rate-limiting-headers)
- [Idempotency Key](#idempotency-key)

## Pagination

### Cursor-based (recommended for large datasets)
```yaml
components:
  schemas:
    ResourcePage:            # the default page shape, same as SKILL.md Step 3
      type: object
      required: [items, next_cursor]
      properties:
        items:
          type: array
          items: {}
        next_cursor:
          type: string
          nullable: true
          example: "eyJpZCI6MTAwfQ"

  parameters:
    CursorParam:
      name: cursor
      in: query
      schema:
        type: string
    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        format: int32
        minimum: 1
        maximum: 100
        default: 20
```

### Offset-based
```yaml
components:
  schemas:
    OffsetPage:
      type: object
      required: [items, total, page, page_size]
      properties:
        items:
          type: array
          items: {}
        total:
          type: integer
          format: int64
        page:
          type: integer
          format: int32
        page_size:
          type: integer
          format: int32
        total_pages:
          type: integer
          format: int32

  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1
    PageSizeParam:
      name: page_size
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
```

---

## Problem Details (RFC 9457, obsoletes RFC 7807)

Standard error body format, media type `application/problem+json` — use
instead of ad-hoc error schemas. `SKILL.md` Step 3 defines the same `Problem`
schema with the `code` member; this is the fuller variant:

```yaml
components:
  schemas:
    Problem:
      type: object
      properties:
        type:
          type: string
          format: uri-reference
          example: https://errors.example.invalid/not-found
        title:
          type: string
          example: Resource Not Found
        status:
          type: integer
          example: 404
        detail:
          type: string
          example: User with id '123' does not exist.
        instance:
          type: string
          format: uri-reference
          example: /users/123
        code:
          type: string
          description: SRS use-case exception name
          example: USER_NOT_FOUND
        errors:
          type: object
          additionalProperties:
            type: array
            items:
              type: string
          description: Field-level validation errors. Extension member (RFC 9457 §3.2)

  responses:
    BadRequest:
      description: Validation error
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    Forbidden:
      description: Insufficient permissions
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    InternalError:
      description: Unexpected server error
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
```

---

## File Upload

### Multipart form (file + metadata)
```yaml
paths:
  /uploads:
    post:
      summary: Upload a file
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                  description: File to upload (max 10MB)
                description:
                  type: string
                  maxLength: 500
                tags:
                  type: array
                  items:
                    type: string
            encoding:
              file:
                contentType: image/png, image/jpeg, application/pdf
      responses:
        "201":
          description: File uploaded
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UploadedFile"
```

### Binary upload (raw body)
```yaml
paths:
  /files/{fileId}/content:
    put:
      summary: Replace file content
      parameters:
        - name: fileId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      responses:
        "204":
          description: Content replaced
```

---

## Callbacks

OpenAPI 3.0 has no top-level `webhooks:` key. An inbound call the API
asks the client to receive is a `callbacks` entry on the operation that
registers it. Do not emit `webhooks:`.

```yaml
paths:
  /orders:
    post:
      operationId: createOrder
      responses:
        "201":
          description: Order created
      callbacks:
        orderCreated:
          "{$request.body#/callback_url}":
            post:
              summary: New order notification
              parameters:
                - $ref: "#/components/parameters/WebhookSignature"
                - $ref: "#/components/parameters/WebhookTimestamp"
              requestBody:
                required: true
                content:
                  application/json:
                    schema:
                      $ref: "#/components/schemas/OrderEvent"
              responses:
                "200":
                  description: Webhook acknowledged
                "401":
                  description: Missing or invalid signature
```

### Webhook signature verification

Every inbound webhook needs a way for the receiver to prove the sender is
who it claims — an unsigned webhook is an unauthenticated write endpoint.
Document the header, not just the payload:

```yaml
components:
  parameters:
    WebhookSignature:
      name: X-Webhook-Signature
      in: header
      required: true
      description: |
        HMAC-SHA256 of the raw request body, hex-encoded, using the
        per-endpoint signing secret. Verify before parsing the body;
        reject with 401 on mismatch — do not process on a bad signature.
      schema:
        type: string
        example: "sha256=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e1e08d5"
    WebhookTimestamp:
      name: X-Webhook-Timestamp
      in: header
      required: true
      description: |
        Unix timestamp the payload was signed at. Reject if outside a
        tolerance window (e.g. 5 minutes) to block replay of a captured
        signed request.
      schema:
        type: string
```

Include the timestamp in the signed payload (`timestamp + "." + body`), not
just the body alone — a signature over the body only does not prevent replay.

---

## HATEOAS Links

```yaml
components:
  schemas:
    Link:
      type: object
      properties:
        href:
          type: string
          format: uri
        rel:
          type: string
        method:
          type: string
          enum: [GET, POST, PUT, PATCH, DELETE]

    ResourceWithLinks:
      allOf:
        - $ref: "#/components/schemas/Resource"
        - type: object
          properties:
            _links:
              type: object
              additionalProperties:
                $ref: "#/components/schemas/Link"
              example:
                self:
                  href: /users/123
                  rel: self
                  method: GET
                update:
                  href: /users/123
                  rel: update
                  method: PATCH
```

---

## Sorting and Filtering

```yaml
components:
  parameters:
    SortParam:
      name: sort
      in: query
      description: "Sort field, prefix with - for descending. E.g. -created_at,name"
      schema:
        type: string
        example: "-created_at"

    FilterParam:
      name: filter
      in: query
      description: "Filter expression. E.g. status=active&role=admin"
      style: deepObject
      explode: true
      schema:
        type: object
        additionalProperties:
          type: string
```

---

## Versioning Patterns

Only for an API with external consumers (SKILL.md, Step 2 → Contract
version). An API called only by the project's own client has no version in
the path, and its `info.version` is the service version.

### Major in the path
```yaml
info:
  version: "2.1.0"   # the contract's own SemVer; its major is the newest path
servers:
  - url: /v1   # relative; a host only when the SRS or the user named it
  - url: /v2
```

A breaking change opens the next major path beside the old one. The old
major's operations stay, marked `deprecated: true`, until its announced
sunset; an addition raises the minor inside the current major. Header or
query-parameter versioning only when the existing spec already uses it.

---

## Rate Limiting Headers

Document rate limit headers in responses:
```yaml
components:
  headers:
    X-RateLimit-Limit:
      description: Maximum requests per window
      schema:
        type: integer
    X-RateLimit-Remaining:
      description: Remaining requests in current window
      schema:
        type: integer
    X-RateLimit-Reset:
      description: UTC epoch seconds when window resets
      schema:
        type: integer
        format: int64
```

Apply to responses:
```yaml
responses:
  "200":
    headers:
      X-RateLimit-Limit:
        $ref: "#/components/headers/X-RateLimit-Limit"
      X-RateLimit-Remaining:
        $ref: "#/components/headers/X-RateLimit-Remaining"
      X-RateLimit-Reset:
        $ref: "#/components/headers/X-RateLimit-Reset"
```

---

## Idempotency Key

```yaml
components:
  parameters:
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: false
      description: |
        Client-generated UUID for idempotent POST requests.
        Same key returns cached response if request was already processed.
      schema:
        type: string
        format: uuid
        example: 123e4567-e89b-12d3-a456-426614174000
```