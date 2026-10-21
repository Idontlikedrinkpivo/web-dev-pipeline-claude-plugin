# React — так / не так

Screens from the room-booking sample (S-1 «Расписание переговорных»).

## Computed, not stored; data through the data layer

```tsx
// не так
const [title, setTitle] = useState("")
useEffect(() => setTitle(`${room.name}, ${formatDate(date)}`), [room, date])
useEffect(() => {
  fetch(`/api/schedule?date=${date}`).then((r) => r.json()).then(setSchedule)
}, [date])

// так
const title = `${room.name}, ${formatDate(date)}`
const schedule = useSchedule(date) // features/schedule/api.ts — TanStack Query over getSchedule
```

## A page is a data hook and a view

```tsx
// не так — one component with the requests, the state and the markup

// так
export function SchedulePage() {
  const data = useSchedulePage()        // queries, mutations, derived values
  return <ScheduleView {...data} />     // props in, JSX out; testable without the network
}
```

## State that cannot contradict itself

```tsx
// не так
const [isCancelling, setIsCancelling] = useState(false)
const [cancelError, setCancelError] = useState<string | null>(null)
const [cancelled, setCancelled] = useState(false)

// так
const cancel = useCancelBooking()       // the mutation's own status: idle | pending | error | success
```

## What the user may do comes from the response

```tsx
// не так — ownership re-derived on the screen
{booking.residentId === session.userId && <CancelButton id={booking.id} />}

// так — the schedule answer says it (`is_mine`)
{booking.is_mine && <CancelButton id={booking.id} />}
```

## Reset with a key, not an effect

```tsx
// не так
useEffect(() => { form.reset(defaultsFor(roomId)) }, [roomId])

// так
<BookingForm key={roomId} defaults={defaultsFor(roomId)} />
```
