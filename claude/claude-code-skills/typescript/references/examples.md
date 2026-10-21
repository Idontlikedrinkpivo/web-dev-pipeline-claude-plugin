# TypeScript — так / не так

## Errors: a kind, a cause, an exhaustive answer

```ts
// не так — empty classes, a swallowed cause, a mapper that forgets a case
export class StorageWriteFailed extends DomainError {}
try { await storage.put(key, bytes) } catch { return }

// так
export class StorageWriteFailed extends Error {
  readonly kind = "StorageWriteFailed" as const
  readonly op: "put" | "delete"
  constructor(op: "put" | "delete", options: { cause: unknown }) {
    super(`storage ${op} failed`, options)
    this.op = op
  }
}
try { await storage.put(key, bytes) } catch (e) { throw new StorageWriteFailed("put", { cause: e }) }

type CancelError = NotFound | Forbidden | StorageWriteFailed

function toStatus(e: CancelError): number {
  switch (e.kind) {
    case "NotFound": return 404
    case "Forbidden": return 403
    case "StorageWriteFailed": return 500
    default: return assertNever(e)
  }
}

export function assertNever(x: never): never {
  throw new Error(`unhandled: ${JSON.stringify(x)}`)
}
```

## State: impossible combinations cannot be written

```ts
// не так
type Load = { isLoading: boolean; error?: string; data?: Booking[] }

// так
type Load =
  | { status: "loading" }
  | { status: "error"; error: string }
  | { status: "ready"; data: readonly Booking[] }
```

## One rule, one home

```ts
// не так — the 30-minute rule (BR-2 in the room-booking sample) typed again in the form
const ok = start.getMinutes() % 30 === 0

// так — the form imports the one module the domain model names for it
import { isHalfHourStep } from "@/shared/booking-rules"
const ok = isHalfHourStep(start)
```

## Promises

```ts
// не так
button.onclick = async () => { await cancel(id) }   // the rejection is lost
ids.forEach(async (id) => { await cancel(id) })      // nobody waits

// так
button.onclick = () => { void cancel(id).catch(report) }  // explicit: fire, and report the failure
await Promise.all(ids.map((id) => cancel(id)))
```
