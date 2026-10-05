# Example — views embedded in the foundation

Read this when unsure where a view goes in `architecture.md` or how a
skipped view reads. Below: the parts of a finished foundation
(`documentation/architecture/architecture.md`) that carry the views, for
a single-process system with one area, then the source of one view.
Everything between the embeds is abbreviated; the sections themselves
follow `output-template-foundation.md`.

```markdown
## 1. Состав системы

![Контекст](diagrams/context.svg)

Один процесс — `IndoorNav`; схемы контейнеров нет.

### Акторы

| Актор | Кто это |
|---|---|
| `Visitor` | … |
| `Admin` | … |

### Хранилища

| Хранилище | Для чего |
|---|---|
| postgres | … |
| svg-store | … |

![Хранилища](diagrams/stores.svg)

### Внешние системы
…

## 2. Модули и функциональные области

| Область | Модуль | Группа SRS | Документ сценариев | … |
|---|---|---|---|---|
| `venues` | `src/venues/` | … | `scenarios/venues/venues.md` | … |

Одна область; схемы модулей нет.

## 3. Границы и поток данных

| Слой | … |
|---|---|
| … | … |

![Слои](diagrams/layers.svg)

…
```

Files on disk for this foundation: `diagrams/context.d2` / `.svg`,
`diagrams/stores.d2` / `.svg`, `diagrams/layers.d2` / `.svg` — no
`containers.*`, no `modules.*`. Source of `diagrams/context.d2`:

```
vars: {
  d2-config: {
    layout-engine: elk
  }
}
direction: right

visitor: Visitor {shape: person}
admin: Admin {shape: person}
sys: IndoorNav
db: postgres {shape: cylinder}
files: "svg-store" {shape: stored_data}
osm: osm

visitor -> sys: "HTTPS"
admin -> sys: "HTTPS"
sys -> db: "SQL"
sys -> files: "S3 API"
sys -> osm: "HTTPS, тайлы"
```
