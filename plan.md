# text2sql — Generative Business Intelligence Chat Tool

## Vision

A chat-based generative BI application where users interact with their data through natural language. The application uses an LLM-powered agent (via DeepAgents + LiteLLM) to understand questions, generate SQL, query datasets via DuckDB, and return results as rich artifacts: charts, tables, narratives, dashboards, and eventually slide decks and videos. All artifacts are persistable, composable into dashboards with cross-filtering, and organizable into collections.

The agent always thinks in **storytelling with data narratives** — choosing the best format to answer each question, not just raw numbers.

---

## Stack

### Frontend (TypeScript)

| Library | Role |
|---------|------|
| **Vite + React** | Build tool + UI framework |
| **json-render** (`@json-render/core`, `@json-render/react`) | Generative UI — AI generates JSON specs, React renders them |
| **Lit** | Web components for visualization primitives (charts, tables, metrics) |
| **@lit/react** (`createComponent`) | Universal React wrapper for Lit elements → json-render registry |
| **Chart.js** | Canvas-based charting inside Lit shadow DOM |
| **Zustand** | UI state management (chat messages, filters, sidebar) |
| **React Router** | Client-side routing |
| **Reveal.js** *(later)* | Slide deck rendering |
| **Remotion** *(later)* | Video generation |

### Backend (Python)

| Library | Role |
|---------|------|
| **FastAPI** | REST + SSE streaming API |
| **DeepAgents** | Agent harness — planning, tool calling, context management, sub-agents |
| **LiteLLM** | Model-agnostic LLM provider (OpenAI, Claude, local, etc.) |
| **DuckDB** | In-process OLAP engine — directly queries CSV, Parquet, JSON files |
| **Motor** | Async MongoDB driver |
| **Boto3 / aiobotocore** | S3 file ingestion |
| **LangGraph** | Underlying graph runtime for DeepAgents |

### Data Stores

| Store | What it holds |
|-------|---------------|
| **MongoDB** | App state: questions, dashboards, collections, conversations, datasets metadata |
| **DuckDB** | Analytics data: registered tables, query execution, ad-hoc file queries |
| **S3** *(optional)* | Source files (CSV, Parquet, JSON) for ingestion |

---

## Architecture

### Monorepo Layout

```
text2sql/
├── frontend/          # Vite + React + Lit (pnpm workspace)
├── backend/           # Python (uv + FastAPI)
├── package.json       # pnpm workspace root
├── pyproject.toml     # Root project pointer
├── plan.md            # This file
└── .gitignore
```

**pnpm workspaces** for frontend (TypeScript monorepo). Backend is a sibling Python project sharing only the git repo.

---

## Backend Architecture

### Clean Architecture — Package by Component

Each component has **four layers**:

| Layer | Responsibility | Depends on |
|-------|---------------|-----------|
| **domain/** | Entities, value objects, domain logic/rules | Nothing (pure Python) |
| **application/ports/** | Protocol interfaces (ports) | Domain layer |
| **application/use_cases/** | Use cases (Command pattern), request DTOs | Domain + application ports |
| **exceptions/** | One file per exception class | Nothing |
| **infrastructure/** | Adapters: repositories, executors, external APIs, **FastAPI routers** | Application ports + shared infrastructure |

Routers live in `infrastructure/fastapi/router.py` per component — not in a separate `presentation/` layer.

A **shared/** package provides cross-cutting base types and infrastructure singletons — no domain of its own.

```
backend/src/
├── main.py                         # FastAPI app — mounts all component routers
├── shared/
│   ├── domain/
│   │   └── base.py                 # Entity, ValueObject, AggregateRoot, DomainEvent
│   └── infrastructure/
│       ├── mongo_client.py         # AsyncMotor client singleton
│       └── duckdb_pool.py          # Thread-safe DuckDB connection pool
├── agent/                          # Chat agent orchestration
│   ├── exceptions/
│   │   ├── conversation_order_error.py
│   │   └── closed_conversation_error.py
│   ├── domain/
│   │   ├── entities.py             # AgentConfig, Message, Conversation
│   │   └── value_objects.py        # ResponseFormat, ToolCall, QueryResult
│   ├── application/
│   │   ├── ports/
│   │   │   ├── i_conversation_repository.py
│   │   │   ├── i_language_model_provider.py
│   │   │   ├── i_tool_executor.py
│   │   │   ├── i_tool_kit.py
│   │   │   ├── i_agent_orchestrator.py
│   │   │   └── i_summarizer.py
│   │   └── use_cases/
│   │       ├── handle_chat_message.py
│   │       └── replay_conversation.py
│   ├── infrastructure/
│   │   ├── fastapi/router.py       # POST /api/v1/chat (SSE)
│   │   ├── deep_agents.py          # DeepAgents harness
│   │   ├── litellm_provider.py     # LiteLLM adapter
│   │   └── tools/
│   │       ├── sql_generator.py    # Text-to-SQL generation
│   │       └── viz_selector.py     # Chooses chart/table/text/dashboard
├── questions/                      # Saved question artifacts
│   ├── exceptions/
│   │   ├── invalid_query_error.py
│   │   ├── same_visualization_error.py
│   │   ├── question_not_found_error.py
│   │   ├── duplicate_question_error.py
│   │   ├── dataset_not_found_error.py
│   │   └── incompatible_questions_error.py
│   ├── domain/
│   │   ├── entities.py             # Question, QueryDefinition
│   │   └── value_objects.py        # QuestionTitle, SqlQuery, VizSpec
│   ├── application/
│   │   ├── ports/
│   │   │   ├── i_question_repository.py
│   │   │   ├── i_query_executor.py
│   │   │   └── i_viz_spec_builder.py
│   │   └── use_cases/
│   │       ├── save_question_from_chat.py
│   │       ├── drill_down_question.py
│   │       ├── compare_questions.py
│   │       └── refresh_stale_questions.py
│   ├── infrastructure/
│   │   ├── fastapi/router.py       # CRUD /api/v1/questions
│   │   └── mongo_repository.py
├── dashboards/                     # Composed dashboards with cross-filtering
│   ├── exceptions/
│   │   ├── tile_overlap_error.py
│   │   ├── tile_not_found_error.py
│   │   ├── self_filter_error.py
│   │   └── dashboard_not_found_error.py
│   ├── domain/
│   │   ├── entities.py             # Dashboard, DashboardLayout, DashboardTile
│   │   └── value_objects.py        # TilePosition, FilterBinding
│   ├── application/
│   │   ├── ports/
│   │   │   ├── i_dashboard_repository.py
│   │   │   ├── i_cross_filter_service.py
│   │   │   └── i_query_executor.py
│   │   └── use_cases/
│   │       ├── apply_cross_filter.py
│   │       └── compose_dashboard.py
│   ├── infrastructure/
│   │   ├── fastapi/router.py       # CRUD /api/v1/dashboards
│   │   └── mongo_repository.py
├── datasets/                       # Data sources
│   ├── exceptions/
│   │   ├── unsupported_format_error.py
│   │   └── duplicate_dataset_name_error.py
│   ├── domain/
│   │   ├── entities.py             # Dataset, SchemaDefinition
│   │   └── value_objects.py        # ColumnDefinition, StorageUri, FileFormat
│   ├── application/
│   │   ├── ports/
│   │   │   ├── i_dataset_repository.py
│   │   │   ├── i_storage_ingestion.py
│   │   │   └── i_query_engine.py
│   │   └── use_cases/
│   │       └── ingest_file.py
│   ├── infrastructure/
│   │   ├── fastapi/router.py       # CRUD /api/v1/datasets
│   │   ├── mongo_repository.py
│   │   ├── duckdb_executor.py      # Schema registration + query execution
│   │   └── s3_ingester.py          # S3 file → DuckDB ingestion
└── collections/                    # Cross-component artifact grouping
    ├── exceptions/
    │   └── collection_not_found_error.py
    ├── domain/
    │   ├── entities.py             # Collection, CollectionContents
    │   └── value_objects.py        # CollectionItem, ArtifactKind
    ├── application/
    │   ├── ports/
    │   │   ├── i_collection_repository.py
    │   │   └── i_search_port.py
    │   └── use_cases/
    │       ├── organize_artifacts.py
    │       └── merge_collections.py
    ├── infrastructure/
    │   ├── fastapi/router.py       # CRUD /api/v1/collections
    │   └── mongo_repository.py
```

### DuckDB Ownership Rule

- `shared/infrastructure/duckdb_pool.py` — owns the **connection pool** (singleton, no domain logic)
- `datasets/infrastructure/duckdb_executor.py` — owns all **direct DuckDB interaction**: schema registration, table creation, query execution
- All other components (questions, agent) **never touch DuckDB directly** — they call through `datasets/application/ports/` ports

### Dependency Injection

FastAPI `Depends()` with manual wiring. Each use case receives its ports via constructor injection. Infrastructure adapters are wired at the composition root (`main.py` or a `deps.py` module).

```python
# main.py
from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from shared.infrastructure.mongo_client import MongoClientSingleton
from agent.infrastructure.deep_agents import DeepAgentsOrchestrator
from agent.infrastructure.litellm_provider import LiteLLMProvider
from agent.application.use_cases.handle_chat_message import HandleChatMessageUseCase
from agent.infrastructure.fastapi.router import create_chat_router

app = FastAPI()

# Wiring at composition root
mongo = MongoClientSingleton("mongodb://localhost:27017")
engine = DuckDBPool()
llm = LiteLLMProvider()
orchestrator = DeepAgentsOrchestrator(llm)
toolkit = build_toolkit(engine)

handle_chat = HandleChatMessageUseCase(
    conversations=mongo,
    orchestrator=orchestrator,
    toolkit=toolkit,
    summarizer=mongo,
    token_limit=TokenCount(128_000),
)

app.include_router(create_chat_router(handle_chat))
```

### Design Patterns

| Pattern | Where | Why |
|---------|-------|-----|
| **Repository** | All `I*Repository` ports | Abstracts MongoDB behind domain-owned interface |
| **Command** | All `*UseCase` classes | Single-responsibility business transactions |
| **Strategy** | `IVizSpecBuilder`, `IToolExecutor` | Swap viz type / tool without changing client code |
| **Composite** | `IToolKit` | Tools as a collection of `IToolExecutor` |
| **Aggregate Root** | `Conversation`, `Dashboard`, `Question` | Consistency boundaries, domain invariants |
| **Value Object** | `SqlQuery`, `VizSpec`, `TilePosition`, `MessageContent` | Immutable, self-validating, no identity |
| **First-Class Collection** | `Messages`, `Questions`, `Tiles`, `Datasets` | Collection behavior encapsulated |
| **Wrapped Primitive** | `QuestionTitle`, `EntityId`, `Temperature`, `ConversationId` | No raw strings/UUIDs/floats across layer boundaries |
| **Factory** | Domain object construction from external input | Encapsulates creation rules |

---

## Frontend Architecture

### Feature-Sliced Design

```
frontend/src/
├── app/                     # App shell, routing, providers
│   ├── App.tsx              # Router setup
│   ├── main.tsx             # Vite entry — registers Lit components
│   ├── providers.tsx         # json-render provider + router provider
│   └── styles/
│       ├── tokens.css       # Design tokens
│       └── global.css
├── pages/                   # Route-level composition
│   ├── chat/ChatPage.tsx
│   ├── questions/{QuestionsPage,QuestionDetail}.tsx
│   ├── dashboards/{DashboardsPage,DashboardDetail}.tsx
│   └── datasets/{DatasetsPage,DatasetDetail}.tsx
├── features/                # Business features per domain
│   ├── chat/                #{ ui, api, model }
│   ├── question/            #{ ui, api, model }
│   ├── dashboard/           #{ ui, api, model }
│   ├── dataset/             #{ ui, api, model }
│   ├── collection/          #{ ui, api, model }
│   └── visualization/       #{ ui, model }
├── entities/                # Pure type definitions (no UI)
│   ├── question/types.ts
│   ├── dashboard/types.ts
│   ├── dataset/types.ts
│   └── agent/types.ts
├── shared/                  # Shared infrastructure
│   ├── api/client.ts        # Fetch wrapper
│   ├── components/          # UI primitives (Button, Card, Input, etc.)
│   ├── lib/wrapLitComponent.ts  # Lit → React universal wrapper
│   └── types/common.ts
└── widgets/                 # Composable widgets
    └── JsonRender/
        ├── catalog.ts       # json-render BI catalog definitions (zod)
        ├── registry.tsx     # Component registry (React-wrapped Lit elements)
        └── components/      # Lit elements
            ├── BarChart.ts  # <bi-bar-chart>
            ├── LineChart.ts # <bi-line-chart>
            ├── PieChart.ts  # <bi-pie-chart>
            ├── DataTable.ts # <bi-data-table>
            ├── Metric.ts    # <bi-metric>
            └── NarrativeText.ts  # <bi-narrative-text>
```

### Lit + React Wrapper Pattern

Each visualization component is a **Lit web component** (Chart.js inside shadow DOM). The universal wrapper converts them to React components for json-render:

```typescript
// shared/lib/wrapLitComponent.ts
import { createComponent } from '@lit/react';
import * as React from 'react';

export function wrapLitComponent(tagName: string, elementClass: CustomElementConstructor) {
  return createComponent({ tagName, elementClass, react: React, events: {} });
}

// widgets/JsonRender/registry.tsx
import { defineRegistry, Renderer } from '@json-render/react';
import { BarChart } from './components/BarChart';
import { catalog } from './catalog';

const { registry } = defineRegistry(catalog, {
  components: {
    BarChart: wrapLitComponent('bi-bar-chart', BarChart),
    DataTable: wrapLitComponent('bi-data-table', DataTable),
    // ...
  },
});
```

### json-render Catalog (Frontend Schema)

```typescript
// widgets/JsonRender/catalog.ts
import { defineCatalog } from '@json-render/core';
import { schema } from '@json-render/react/schema';
import { z } from 'zod';

export const biCatalog = defineCatalog(schema, {
  components: {
    BarChart: {
      props: z.object({
        title: z.string(),
        xAxis: z.string(),
        yAxis: z.string(),
        data: z.array(z.object({ label: z.string(), value: z.number() })),
        color: z.string().optional(),
      }),
      description: 'Vertical bar chart for comparing values across categories',
    },
    DataTable: {
      props: z.object({
        title: z.string().optional(),
        columns: z.array(z.object({ key: z.string(), header: z.string(), format: z.string().optional() })),
        rows: z.array(z.record(z.any())),
      }),
      description: 'Tabular data display with sortable columns',
    },
    Metric: {
      props: z.object({
        label: z.string(),
        value: z.string(),
        change: z.string().optional(),
        direction: z.enum(['up', 'down', 'neutral']).optional(),
      }),
      description: 'Single KPI metric with optional trend indicator',
    },
    NarrativeText: {
      props: z.object({
        content: z.string(),
        tone: z.enum(['analytical', 'conversational', 'executive']).optional(),
      }),
      description: 'Data-driven narrative text response',
    },
  },
  actions: {
    save_as_question: { description: 'Save response as a question artifact' },
    add_to_dashboard: { description: 'Add this viz to a dashboard' },
    export_data: { description: 'Export underlying data as CSV' },
    drill_down: { description: 'Filter by a dimension value' },
  },
});
```

---

## Data Flow: Chat → Visualization

```
User: "Show me revenue by quarter for 2025"

POST /api/v1/chat  ──SSE──→  HandleChatMessageUseCase
  │
  ├─ Conversation.load() → Conversation.add_user_message()
  │
  ├─ IAgentOrchestrator.run()
  │   ├─ sql_generator tool:
  │   │   LLM writes SQL → IDatasetRepository.load() → IQueryEngine.execute()
  │   │   → returns QueryResult(columns, rows)
  │   └─ viz_selector tool:
  │       LLM inspects data shape → picks ResponseKind.CHART
  │       → returns json-render spec as AgentEvent(spec_fragment)
  │
  └─ SSE stream → SpecStreamCompiler → <Renderer> → <bi-bar-chart>
                                                          │
                                                      Chart.js canvas
                                                          │
                                              User clicks "Save as question"
                                                          │
                                              POST /api/v1/questions
                                              → SaveQuestionFromChatUseCase
                                                  → deduplicates by SQL hash
                                                  → persists to MongoDB
```

---

## Endpoint Map

| Method | Path | Component | Use Case |
|--------|------|-----------|----------|
| `POST` | `/api/v1/chat` | agent | `HandleChatMessageUseCase` (SSE stream) |
| `GET` | `/api/v1/questions` | questions | List all questions |
| `POST` | `/api/v1/questions` | questions | `SaveQuestionFromChatUseCase` |
| `GET` | `/api/v1/questions/{id}` | questions | Load single question |
| `DELETE` | `/api/v1/questions/{id}` | questions | Delete question |
| `POST` | `/api/v1/questions/{id}/drill` | questions | `DrillDownQuestionUseCase` |
| `POST` | `/api/v1/questions/compare` | questions | `CompareQuestionsUseCase` |
| `GET` | `/api/v1/dashboards` | dashboards | List dashboards |
| `POST` | `/api/v1/dashboards` | dashboards | `ComposeDashboardFromQuestionsUseCase` |
| `GET` | `/api/v1/dashboards/{id}` | dashboards | Load dashboard + execute all tiles |
| `POST` | `/api/v1/dashboards/{id}/filter` | dashboards | `ApplyCrossFilterUseCase` |
| `DELETE` | `/api/v1/dashboards/{id}` | dashboards | Delete dashboard |
| `GET` | `/api/v1/datasets` | datasets | List datasets |
| `POST` | `/api/v1/datasets` | datasets | Register table or connection |
| `POST` | `/api/v1/datasets/ingest` | datasets | `IngestFileUseCase` |
| `GET` | `/api/v1/datasets/{id}/preview` | datasets | Preview data (LIMIT 100) |
| `DELETE` | `/api/v1/datasets/{id}` | datasets | Unregister dataset |
| `GET` | `/api/v1/collections` | collections | List collections |
| `POST` | `/api/v1/collections` | collections | `OrganizeArtifactsIntoCollectionUseCase` |
| `GET` | `/api/v1/collections/{id}` | collections | Load collection with items |
| `POST` | `/api/v1/collections/merge` | collections | `MergeCollectionsUseCase` |
| `DELETE` | `/api/v1/collections/{id}` | collections | Delete collection |

---

## Object Calisthenics (Jeff Bay) — Applied

| Rule | How Applied |
|------|-------------|
| 1. One indent level per method | Every method ≤ 1 level deep; branching delegated to helper methods |
| 2. Don't use ELSE | Early returns, strategy dispatch, `if`-guards with return |
| 3. Wrap all primitives | No raw `str`, `int`, `UUID`, `float`, `datetime` in signatures |
| 4. First-class collections | `Messages`, `Questions`, `Tiles`, `Datasets` — each wraps `list[T]` with domain methods |
| 5. One dot per line | `self._repository.save(question)` — never `a.b.c.d()` |
| 6. Don't abbreviate | `EntityId`, `MessageContent`, `QueryDefinition`, `ConversationId` — never `ID`, `Msg`, `Conv` |
| 7. Keep entities small | No entity > ~25 lines; complex logic split into methods or extracted |
| 8. Max 2 instance variables | `Question(_identity, _specification)`, `Message(_identity, _body)`, `Dataset(_identity, _configuration)` |
| 9. No getters/setters | `Question.rename(new_title)`, `Conversation.add_user_message()`, `QueryDefinition.with_filter()` — behavior, not property access |

---

## Design Rules

1. **Entities contain pure domain logic** — rules that don't need I/O (SQL validation, tile overlap detection, turn order enforcement, viz change validation)
2. **Use cases are business transactions** — not CRUD wrappers (deduplication, drift detection, cross-filter propagation, auto-layout with filter binding)
3. **Ports are defined by the consumer** — application layer defines interfaces, infrastructure implements them (Dependency Inversion)
4. **DuckDB accessed through one component only** — `datasets` owns all query execution; questions/agent call through ports
5. **No anemic domain** — entities have behavior: `Question.derive_drill_down()`, `Conversation.should_summarize()`, `DashboardLayout.tiles_affected_by()`
6. **Streaming is first-class** — chat responses stream via SSE as json-render SpecStream fragments; frontend renders progressively

---

## Implementation Order

| Step | What | Why First |
|------|------|-----------|
| 1 | Scaffold: monorepo, tsconfig, vite, pyproject, directory tree | Foundation |
| 2 | Backend shared: base.py, mongo_client, duckdb_pool | Everything depends on these |
| 3 | Backend datasets: domain → use cases → infra → routes | Data must exist before questions |
| 4 | Backend agent: domain → use cases → infra (deep_agents + tools) → routes | Core AI pipeline |
| 5 | Backend questions: domain → use cases → infra → routes | Persist chat results |
| 6 | Backend dashboards: domain → use cases → infra → routes | Composite artifacts |
| 7 | Backend collections: domain → use cases → infra → routes | Cross-component grouping |
| 8 | Frontend shared: design tokens, UI primitives, API client, Layout | App skeleton |
| 9 | Frontend Lit components: BarChart, LineChart, DataTable, Metric, Text | Core viz building blocks |
| 10 | Frontend json-render: wrapLitComponent → catalog → registry | Bridge Lit → json-render |
| 11 | Frontend chat: ChatPage with SSE streaming + Zustand store | Main user interaction |
| 12 | Frontend questions: list + detail pages | Artifact browsing |
| 13 | Frontend dashboards: grid layout + cross-filtering | Composite artifacts |
| 14 | Frontend datasets: registration + schema browsing | Data management |
| 15 | Frontend collections: organize artifacts | Final feature |
