# Resource design — paths and methods

Read before writing `paths`. One use case is one operation (SKILL.md, Step 1); this file says which path and which
method it gets. Without it every project's writer picked them from habit, and the same kind of use case came out
as `POST /bookings/{id}/cancel` in one spec, `PATCH status` in the next and `/cancelBooking` in a third.

## Contents

- [Paths](#paths)
- [Methods](#methods)
- [Actions — a use case that is not create, change or delete](#actions--a-use-case-that-is-not-create-change-or-delete)
- [Repeats and idempotency](#repeats-and-idempotency)
- [Bodies](#bodies)
- [An existing spec](#an-existing-spec)

## Paths

- **A resource is a plural noun:** `/bookings`, `/rooms`. A verb never names a collection or an item
  (`/getBookings`, `/createBooking`, `/bookings/list`) — the method says what is done.
- **A segment of several words is kebab-case:** `/meeting-rooms`. Path parameters, query parameters and properties
  stay `snake_case` (Step 3); the literal segments are the one place with hyphens.
- **One item:** `/bookings/{booking_id}` — the parameter is `<resource>_id` and carries the `public_id`
  (`db-schema-design` → How the API names keys).
- **Nesting — one level, for what belongs to a parent:** `/rooms/{room_id}/bookings` lists a room's bookings.
  The item itself lives once, at `/bookings/{booking_id}`, never at `/rooms/{room_id}/bookings/{booking_id}`.
- **A filter is a query parameter, not a path:** `GET /bookings?room_id=…&date=2026-11-03`, not
  `/rooms/{room_id}/bookings/today` (sorting and filters — `common-patterns.md` → Sorting and Filtering).
- **The caller's own things — `/me`:** «мои брони» is `GET /me/bookings`; the user comes from the authentication,
  never from a `user_id` in the path the client could change (that is how one user reads another's data). A
  resource there is one of a kind: `GET /me/settings`, `PATCH /me/settings`.
- No trailing slash, no extension (`/bookings.json`), no version in the path unless the API has external consumers
  (Step 2 → Contract version).

## Methods

| Method | Use | Repeating it | Success |
|---|---|---|---|
| `GET` | Read an item or a list. Never changes stored data — not «mark as read», not a status | safe | `200` |
| `POST` on a collection | Create an item; the server issues its `id` | creates again — see Repeats | `201`, the created item |
| `PATCH` on an item | Change some fields: an absent field stays as it is; `null` clears a field only where the schema allows null | same result | `200`, the item |
| `PUT` on an item | Replace the item whole: the body carries every field the client may set, an absent one is reset. Only when the use case sends the whole item — a settings form saved at once | same result | `200`, the item |
| `DELETE` on an item | Remove it (a soft deletion the schema keeps is still `DELETE`) | same result | `204` |

The default for editing is `PATCH`: a form usually changes a few fields, and `PUT` would reset the ones it does not
send. Status codes beyond the success one — Step 6.

## Actions — a use case that is not create, change or delete

«Отменить бронь», «отправить на согласование», «утвердить», «отправить письмо повторно» move the resource along
its states under rules: who may, from which state, what else happens. Such a use case is an **action**:

- `POST /bookings/{booking_id}/cancel` — the use case's verb as the last segment, after the item; this is the one
  place a verb is in a path. `operationId` is the same verb (`cancelBooking`). The body carries only what the use
  case takes (a reason), or there is none. Success is `200` with the changed item.
- **Not `PATCH` of `status`.** A writable `status` lets the client set any state and hides the transition's rules
  in the server; `status` is read-only in the schema whenever a use case moves it. `PATCH` sets plain fields only.
- **An action that leaves a record read later as a list** — an approval with its comment, a payment — is a
  sub-collection instead: `POST /bookings/{booking_id}/approvals`, `GET /bookings/{booking_id}/approvals`.
- **A computation with nothing stored** — free slots, a price: `GET /rooms/availability?date=…&duration=…` when
  its inputs fit a query; `POST /price-quotes` when they need a body, with `200`, not `201`.
- **Sign-in and the like:** `POST /auth/login`, `POST /auth/logout`, `POST /auth/refresh` — actions on the
  session, under one `/auth` prefix, for whichever of them the SRS's use cases name.

## Repeats and idempotency

A client repeats a request when the network drops the answer. `GET`, `PATCH`, `PUT` and `DELETE` are safe to
repeat by their meaning; a `POST` is not:

- **`Idempotency-Key` is required** (`common-patterns.md` → Idempotency Key, with `required: true`) on a `POST`
  whose duplicate does harm: money moves, an order or a booking is taken for a limited resource, a message leaves
  the system — and wherever the SRS says a duplicate must not appear. The same key returns the first answer.
- **Optional or none** on a plain create the user would notice and remove themselves.
- **An action repeated** returns its result again when the state is already there: cancelling a cancelled booking
  is `200` with the item, unless the SRS names that case an error (then its named error and status, Step 6).

## Bodies

- A request body is a JSON object — never a bare array or a scalar: `{"items": [...]}` takes a field later
  without breaking clients.
- What the server sets — `id`, timestamps, the owner, a status moved by actions — is `readOnly: true` in the schema
  and never accepted from the client.
- Create, change and action responses return the item as `GET` returns it, so the client does not read it again.

## An existing spec

The rules hold for every new operation. An existing path or method that breaks one stays: renaming it is a
`ломает` change (Step 1b) for a style gain. Name it in CONCERNS — the user decides whether it goes into a release
with its client. A new operation keeps the spec's own form where it has one (a spec already using `snake_case`
segments keeps them) and follows this file where it has none.
