# A filled unit

Read at Step 4, for calibration: match its density, not its domain.

```markdown
### U4. Добавить переход заказа Draft → Paid

| | |
|---|---|
| **Документы** | scenarios/orders/01-orders.md `PayOrder` · domain §4 инвариант «оплаченный заказ неизменяем» · SRS UC-2 / AC-2.1 / AC-Exc-1 · BR-3 |
| **Файлы** | `src/orders/domain/order.ts` · `src/orders/domain/order.test.ts` |
| **Меняет символы** | `Order.addLine()` — у оплаченного заказа теперь бросает `IllegalTransition` |
| **Не затрагивается** | `src/orders/application/add-order-line.ts` — доменные ошибки уже пробрасывает наружу без перехвата (поиск `addLine`: других вызовов нет) |
| **Образец** | `src/invoices/domain/invoice.ts` — переход состояния и доменная ошибка |
| **Зависит от** | U2 |
| **Параллельно** | no — U5 тоже правит `src/orders/domain/order.ts` |
| **Сложность** | Low |
| **Почему** | rule 5 — переход задан BR-3, прецедент в invoice |
| **Исполнитель** | impl-lite |
| **Вложенный** | — |
| **Что делает вложенный** | — |

**Цель** — у `Order` есть метод `pay()`: Draft → Paid, любой переход из Paid запрещён.

**Подход** — метод и ошибка `IllegalTransition` названы в domain §2 `Order` и scenarios/orders/01-orders.md `PayOrder`;
событие `OrderPaid` возвращается, а не публикуется (публикация — U7).

**Тестовые сценарии**
- заказ Draft на 100 → `pay()` → статус Paid, возвращён `OrderPaid{orderId, amount: 100}` (AC-2.1)
- заказ Paid → `pay()` → `IllegalTransition`, статус остаётся Paid (covers BR-3, AC-Exc-1)
- заказ Paid → `addLine()` → `IllegalTransition` (covers BR-3)

**Проверка** — из Paid нет ни одного разрешённого перехода; тесты агрегата зелёные.

**Коммит** — `feat(order): add Draft→Paid transition`
```
