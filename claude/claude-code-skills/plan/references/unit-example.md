# A filled unit

Read at Step 4, for calibration: match its density, not its domain.

```markdown
### U4. Добавить переход заказа Draft → Paid

| | |
|---|---|
| **Docs** | scenarios/orders `PayOrder` · domain §4 инвариант «оплаченный заказ неизменяем» · SRS UC-2 / AC-2.1 / AC-Exc-1 · BR-3 |
| **Files** | `src/domain/order/order.ts` · `src/domain/order/order.test.ts` |
| **Pattern** | `src/domain/invoice/invoice.ts` — переход состояния и доменная ошибка |
| **Depends on** | U2 |
| **Parallel-safe** | no — U5 тоже правит `src/domain/order/order.ts` |
| **Complexity** | Low |
| **Why** | rule 5 — переход задан BR-3, прецедент в invoice |
| **Implementer** | impl-lite |
| **Nested** | — |
| **Nested does** | — |

**Goal** — у `Order` есть метод `pay()`: Draft → Paid, любой переход из Paid запрещён.

**Approach** — метод и ошибка `IllegalTransition` названы в domain §2 `Order` и scenarios/orders `PayOrder`;
событие `OrderPaid` возвращается, а не публикуется (публикация — U7).

**Test scenarios**
- заказ Draft на 100 → `pay()` → статус Paid, возвращён `OrderPaid{orderId, amount: 100}` (AC-2.1)
- заказ Paid → `pay()` → `IllegalTransition`, статус остаётся Paid (covers BR-3, AC-Exc-1)
- заказ Paid → `addLine()` → `IllegalTransition` (covers BR-3)

**Verification** — из Paid нет ни одного разрешённого перехода; тесты агрегата зелёные.

**Commit** — `feat(order): add Draft→Paid transition`
```
