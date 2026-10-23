# Security Schemes (OpenAPI 3.0)

## Bearer JWT (only when named)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT access token. Obtain via /auth/token.
        Include as: Authorization: Bearer <token>

security:
  - BearerAuth: []
```

## API Key — Header

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key issued from the developer portal.

security:
  - ApiKeyAuth: []
```

## OAuth 2.0 — Authorization Code

The URLs are the identity provider's, from the SRS or the user — never a
placeholder host shipped as the contract (SKILL.md → Step 2). Without
one, the flow is a BLOCKED question.

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://<auth host the SRS names>/oauth/authorize
          tokenUrl: https://<auth host the SRS names>/oauth/token
          refreshUrl: https://<auth host the SRS names>/oauth/refresh
          scopes:
            read:users: Read user profiles
            write:users: Create and update users
            admin: Full administrative access

security:
  - OAuth2: [read:users]
```

## OAuth 2.0 — Client Credentials (machine-to-machine)

```yaml
components:
  securitySchemes:
    ClientCredentials:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://<auth host the SRS names>/oauth/token
          scopes:
            api:read: Read access
            api:write: Write access
```

## OpenID Connect

```yaml
components:
  securitySchemes:
    OpenIDConnect:
      type: openIdConnect
      openIdConnectUrl: https://<auth host the SRS names>/.well-known/openid-configuration
```

## Multiple Schemes (AND — both required)

```yaml
security:
  - ApiKeyAuth: []
    BearerAuth: []
```

## Multiple Schemes (OR — either works)

```yaml
security:
  - ApiKeyAuth: []
  - BearerAuth: []
```

## Unspecified / none recorded

When the SRS names no scheme, emit an empty array at the
document root. An omitted `security` key is not the same thing: readers
cannot tell "public" from "author forgot".

```yaml
security: []
```

Do not invent `BearerAuth` / JWT / `securitySchemes` to fill the gap.

## Public endpoint (override global security)

An operation the SRS opens to anyone, under a document whose root `security` requires a token:

```yaml
paths:
  /rooms:
    get:
      operationId: listRooms
      summary: List rooms (public)
      security: []
      responses:
        "200":
          description: OK
```

The service paths (`/health/live`, `/health/ready`, `/metrics`) are not in the contract at all — `repo-scaffold`
builds them and the contract test skips them — so they need no override and get no operation.

Do not emit: API key in query string, HTTP Basic, OAuth password flow, OAuth implicit flow.
