# Base schemas

Read before writing `components` (SKILL.md → Step 3). Each block is the
one copy of its shape: copy it as it stands, adding only the examples of
this product. In the split layout each schema and response is its own
file under `components/` (Step 8 → Layout); the `$ref`s below are the
single-file form.

## Collection page

Keyset by default: query parameters `cursor` (opaque) and `limit`. Offset
paging (`page`, `page_size`, `total`) only when the SRS asks for page
numbers or a total count on screen (`common-patterns.md` → Offset-based).

```yaml
ResourcePage:
  type: object
  required: [items, next_cursor]
  properties:
    items:
      type: array
      items:
        $ref: "#/components/schemas/Resource"
    next_cursor:
      type: string
      nullable: true
      description: null на последней странице
      example: eyJpZCI6MTAwfQ
```

## Error body — RFC 9457 Problem Details

Media type `application/problem+json`. `type` is a relative URI,
`/problems/<code in kebab-case>`: a host appears only when the SRS or the
user named one, as everywhere in the spec. `code` is the SRS exception
name; `errors` exists only on 422 `VALIDATION_ERROR`.

```yaml
Problem:
  type: object
  properties:
    type:
      type: string
      format: uri-reference
      default: about:blank
      example: /problems/hold-limit-reached
    title:
      type: string
      example: Превышен лимит броней
    status:
      type: integer
      format: int32
      example: 409
    detail:
      type: string
    instance:
      type: string
      format: uri-reference
    code:
      type: string
      description: Имя исключения use case из SRS; VALIDATION_ERROR для 422 по полям
      example: HOLD_LIMIT_REACHED
    errors:
      type: array
      description: только у 422 VALIDATION_ERROR — каждое поле, не прошедшее схему
      items:
        type: object
        required: [field, message]
        properties:
          field: { type: string, example: starts_at }
          message: { type: string }
```

## Timestamps mixin

Use with `allOf`.

```yaml
Timestamps:
  type: object
  properties:
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

## Shared responses

Referenced from operations by `$ref` (Step 6 says which operation gets
which). A named use-case error is its own response, not one of these.

```yaml
responses:
  ValidationError:
    description: Поле запроса не прошло схему (VALIDATION_ERROR)
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  BadRequest:
    description: Запрос нельзя разобрать — битый JSON или курсор
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  Unauthorized:
    description: Нужен вход
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  Forbidden:
    description: Недостаточно прав
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  NotFound:
    description: Объект не найден
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  TooManyRequests:
    description: Превышен лимит запросов
    headers:
      Retry-After:
        schema:
          type: integer
        description: Через сколько секунд повторить
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  ServiceUnavailable:
    description: Запись не прошла из-за параллельной транзакции — повторите
    headers:
      Retry-After:
        schema:
          type: integer
        description: Через сколько секунд повторить
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
  InternalError:
    description: Внутренняя ошибка сервера
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
```
