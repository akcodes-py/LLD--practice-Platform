# LLD Practice Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1%2B-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Repository](https://img.shields.io/badge/GitHub-LLD--practice--Platform-orange.svg)](https://github.com/akcodes-py/LLD--practice-Platform)

A focused Low-Level Design (LLD) practice and automated evaluation platform built for the **CipherSchools 2-Day Engineering Assignment (September 2026)**.

The platform guides learners through an iterative design loop:
**Choose a Problem → Formulate Structured Design → Submit → Receive Explainable Rubric Feedback → Review History → Retry & Improve**.

---

## Table of Contents

- [The Learner Problem](#the-learner-problem)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Submission & Evaluation Engine](#submission--evaluation-engine)
- [Core Assignment Design Questions Answered](#core-assignment-design-questions-answered)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Running Tests](#running-tests)
- [REST API Specification](#rest-api-specification)
- [Quality & Pre-Launch Checklist](#quality--pre-launch-checklist)
- [Known Limitations & Roadmap](#known-limitations--roadmap)
- [AI Usage Disclosure](#ai-usage-disclosure)

---

## The Learner Problem

Low-Level Design practice is notoriously easy to start but difficult to evaluate:
1. **Many Valid Solutions**: A Parking Lot can be designed with a central allocator or distributed per-floor managers. Learners often stall wondering *"which one is right?"* instead of analyzing trade-offs.
2. **Vague or Unactionable Feedback**: Feedback typically reduces to an unexplained score or generic compliments, offering no concrete suggestions for the next iteration.
3. **No Retained Iteration History**: Without tracked attempts, learners cannot measure whether their design improved across revisions.
4. **Ambiguous Submission Bar**: Learners struggle to identify what a rigorous design solution must cover (requirements mapping, class contracts, relationships, edge cases).

**Our Product Answer**: Provide 5 interview-grade problems, require a six-section structured design, execute an 8-criterion explainable rubric with quoted evidence, and preserve full attempt history with a one-click retry flow.

---

## Key Features

- **5 Interview-Grade LLD Problems**:
  - *Parking Lot* (Multi-floor, vehicle sizes, dynamic ticketing, strategy allocation)
  - *Elevator System* (Dispatching algorithms, internal/external requests, state transitions)
  - *Vending Machine* (State pattern, inventory tracking, coin/cash transactions, refunds)
  - *Library Management System* (Book cataloging, reservation queue, fine calculation, member limits)
  - *Food Ordering System* (Restaurant menus, cart state, payment processing, delivery tracking)
  Each problem includes functional requirements, scale/hardware constraints, design considerations, and tricky edge cases.

- **Six-Section Structured Text Submission**:
  1. *Requirements & Assumptions*
  2. *Classes & Responsibilities*
  3. *Relationships & Interfaces*
  4. *Workflows & Interactions*
  5. *Trade-offs & Alternatives*
  6. *Edge Cases & Testability*

- **Explainable 8-Criterion Evaluation Rubric**:
  Evaluates:
  1. *Requirement Understanding & Assumptions*
  2. *Single Responsibility & Cohesion*
  3. *Coupling & Class Relationships*
  4. *Encapsulation & Interface Design*
  5. *Appropriate Abstraction & Patterns*
  6. *Extensibility & Trade-off Awareness*
  7. *Edge Case Handling & Testability*
  8. *Explanation Quality & Communication*

  Each criterion yields:
  `score (0-100)` | `evidence (quoted directly from submission)` | `concern` | `actionable suggestion` | `confidence`

- **Honest Provider Labelling**:
  Deterministic rule-based evaluator is clearly labelled as **"Rule-based review"** (never mislabelled as AI). An optional LLM evaluator runs only when configured via backend environment variables (`LLM_ENABLED=1`), with strict JSON schema validation, timeouts, and explicit failure fallback.

- **Resilient Asynchronous Lifecycle**:
  - Submissions are persisted *before* evaluation starts (crash-proof).
  - Lifecycle states: `draft → submitted → evaluating → completed | failed`.
  - Background daemon thread with non-blocking 202 response and 1.5s frontend polling.
  - Idempotent creation and submission (`idempotency_key`).
  - Failed evaluations preserve content and offer instant re-evaluation.
  - Retrying clones the attempt into a new draft while retaining complete history.

- **Polished Learner UI**:
  - Responsive layout (mobile-first, 360px to 4K displays).
  - WCAG-compliant color contrast, keyboard navigation, and visible focus rings.
  - Dynamic page metadata (`title`, `meta description`), social preview (`og:image`), favicon.
  - Custom accessible 404 page, Privacy Policy, Terms & Conditions.
  - Real-time autosave indicators, loading skeletons, and honeypot bot defense.

---

## System Architecture

The system is implemented as a clean, cohesive modular monolith:

```
[ Frontend: React 18 + TypeScript + Vite + Tailwind CSS ]
                       │
             REST API Calls (JSON)
             Vite Dev Proxy / Nginx reverse proxy
                       │
                       ▼
[ Backend: Django 5 + Django REST Framework ]
  ├── practice/views.py        -> Thin HTTP controllers (request parsing & response envelopes)
  ├── practice/services.py     -> Domain rules, validation, attempt lifecycle, async runner
  ├── practice/models.py       -> Problem, Attempt, Evaluation
  └── practice/evaluators/
        ├── base.py            -> Evaluator contract & schema validation
        ├── rule_based.py      -> Deterministic heuristic scoring with text citation
        └── llm.py             -> Optional OpenAI/compatible LLM integration
                       │
                       ▼
[ Persistence Layer: SQLite (Local Dev) / PostgreSQL 16 (Docker Compose) ]
```

### Architectural Principles:
- **Separation of Domain and HTTP**: Views never contain business rules; `services.py` orchestrates transactions, content validation, and background evaluation threads.
- **Strict Evaluator Contract**: Evaluators implement a common output schema (`validate_result` in `evaluators/base.py`). Adding a diagram evaluator or human review system requires zero changes to the submission pipeline.
- **Crash-Safe Persistence**: Attempt records are committed to the database before the background worker thread starts. Even if the process terminates mid-evaluation, the user's work is never lost.

---

## Submission & Evaluation Engine

### Why Structured Text?
Code requires compilation containers and language runtimes; diagram tools require complex canvas editors. Neither directly measures design reasoning. Structured text requires the candidate to articulate their class contracts, relationship choices, and trade-offs directly—which is what interviewers actually evaluate.

### Deterministic vs. Judgment Split
| Layer | Mechanism | Purpose |
|---|---|---|
| Deterministic | Field minimums, word count, state machine transitions, idempotency checks | Reject empty or malicious payloads before evaluation |
| Rule-Based Heuristic (Default) | Section coverage, keyword analysis, design pattern detection, interface usage | Provide fast (<10ms), offline, explainable scoring with exact quotes |
| LLM-Powered (Optional) | Prompt-engineered LLM with structured JSON output | Deeper semantic reasoning on trade-offs and alternative architectures |

---

## Core Assignment Design Questions Answered

### 1. What does a learner actually need to provide for an LLD practice attempt to be meaningful?
A meaningful LLD attempt must capture:
- Scope boundaries and explicit assumptions.
- Core classes and their single responsibilities.
- Interface contracts and relationship types (composition vs inheritance, dependency inversion).
- Execution workflows for key use cases.
- Justified trade-offs and rejected alternatives.
- Edge cases and failure mitigation.
The six-section template enforces this completeness without unnecessary tooling friction.

### 2. What makes feedback useful when there can be more than one valid LLD solution?
- **Rubric over Resemblance**: The system evaluates adherence to design principles (cohesion, coupling, open-closed principle) rather than matching a single reference solution.
- **Quoted Evidence**: Feedback quotes the learner's exact sentences, showing where a concern was observed.
- **Actionable Suggestions**: Each criterion provides a concrete improvement step rather than an abstract score.
- **Non-Penalization of Valid Alternatives**: Alternative architectures (e.g. strategy injection vs state machines) are acknowledged as valid trade-offs.

### 3. Which parts of evaluation should be deterministic vs LLM?
- **Deterministic**: Input presence, section minimum lengths, duplicate detection, lifecycle transitions, and base heuristic grading.
- **LLM**: Nuanced semantic critique of subtle architectural coupling and edge-case sufficiency. The LLM is strictly constrained by a deterministic schema validator.

### 4. How would the design accommodate another evaluation approach or submission format?
- **New Evaluators**: Implement a callable conforming to `evaluators/base.py` output structure and register it in `services._run_evaluator`.
- **New Submission Formats**: The `Attempt` model can store diagram JSON or code snippets as additive fields or an `adapter` payload without breaking the core state lifecycle.

### 5. What happens if evaluation takes time or fails?
- The submit endpoint immediately responds with `202 Accepted` and `status: "evaluating"`.
- The frontend shows an animated evaluation state and polls `/api/attempts/<id>/status/` every 1.5s.
- If an evaluator times out or throws an error, the attempt transitions to `status: "failed"` with a human-readable error description, and a **"Re-evaluate"** button allows immediate retry without re-submitting.

---

## Project Structure

```
lld-practice-platform/
├── backend/                         # Django REST Framework backend
│   ├── config/                      # Project settings, URLs, WSGI
│   │   ├── settings.py              # Environment config, SQLite WAL, CORS, HTTPS
│   │   └── urls.py                  # Root URL configuration
│   ├── practice/                    # Core practice application
│   │   ├── evaluators/              # Evaluation engines
│   │   │   ├── base.py              # Result schema & validation contract
│   │   │   ├── rule_based.py        # Heuristic scoring engine with evidence extraction
│   │   │   └── llm.py               # Optional OpenAI/LLM evaluator
│   │   ├── management/commands/     # Seed commands (seed_problems)
│   │   ├── migrations/              # Database schema migrations
│   │   ├── models.py                # Problem, Attempt, Evaluation entities
│   │   ├── serializers.py           # DRF serializers & validation rules
│   │   ├── services.py              # Business logic, state transitions, async runner
│   │   └── views.py                 # REST API endpoints
│   ├── tests/                       # Pytest test suite (13 tests)
│   ├── manage.py                    # Django management script
│   └── requirements.txt             # Python dependencies
├── frontend/                        # React SPA (TypeScript + Vite + Tailwind)
│   ├── src/
│   │   ├── components/              # Header, Footer, StatusBadge, ScoreBar, Layout
│   │   ├── pages/                   # Home, ProblemList, ProblemDetail, AttemptEditor,
│   │   │                            # AttemptReview, HistoryList, NotFound, Privacy, Terms
│   │   ├── lib/                     # API client, types, meta tag hooks
│   │   └── __tests__/               # Vitest unit & smoke tests (4 tests)
│   ├── index.html                   # HTML entry with meta/OG tags
│   ├── package.json                 # NPM scripts & dependencies
│   ├── tailwind.config.js           # Design tokens & color system
│   └── vite.config.ts               # Vite configuration & dev proxy
├── .github/workflows/               # GitHub Actions CI workflow
├── docker-compose.yml               # Multi-container Docker Compose configuration
├── AI_USAGE.md                      # AI assistance disclosure and rationale
└── README.md                        # Project documentation (this file)
```

---

## Prerequisites

- **Python**: Version 3.12 or newer
- **Node.js**: Version 20 or newer (npm 10+)
- **Docker & Docker Compose** (Optional, for containerized run)

No external API keys are required for core functionality. The deterministic rule-based evaluator runs entirely offline.

---

## Environment Configuration

Copy the example environment files:

```bash
# Root (for Docker Compose)
cp .env.example .env

# Backend (optional for local SQLite development)
cp backend/.env.example backend/.env

# Frontend (optional for local Vite development)
cp frontend/.env.example frontend/.env
```

### Key Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_DEBUG` | `1` | Enable/disable Django debug mode |
| `DJANGO_SECRET_KEY` | Development key | Secret key for Django cryptographic signing |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection string (PostgreSQL in Docker) |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed frontend origins for CORS |
| `LLM_ENABLED` | `0` | Set to `1` to enable optional LLM evaluation |
| `LLM_API_KEY` | `""` | OpenAI/compatible API key (kept backend-only) |
| `VITE_API_URL` | Empty (uses `/api` proxy) | Backend API endpoint URL for frontend |

---

## Local Development Setup

### 1. Backend Setup

Open a terminal and run:

```bash
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed the 5 practice problems (idempotent)
python manage.py seed_problems

# Start development server
python manage.py runserver 127.0.0.1:8000
```
Backend API will be available at: `http://127.0.0.1:8000/api/`

### 2. Frontend Setup

Open a second terminal and run:

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend application will be live at: `http://localhost:5173`

The Vite dev server automatically proxies all `/api/*` requests to `http://127.0.0.1:8000`, so no manual CORS configuration is necessary.

---

## Docker Deployment

To spin up the entire application stack (React SPA via Nginx reverse proxy + Django backend + PostgreSQL 16) with a single command:

```bash
# Set your environment variables
copy .env.example .env

# Build and start containers
docker compose up --build
```

- **Frontend Application**: `http://localhost:8080`
- **Backend API & Health**: `http://localhost:8080/api/health/`
- Migrations and problem seeding execute automatically on startup.

---

## Running Tests

### Backend Tests (Pytest)
Includes 13 tests covering API journeys, validation checks, duplicate prevention, idempotency, failure recovery, and evaluator output contracts:

```bash
cd backend
python -m pytest -v
```

### Frontend Tests (Vitest & TypeScript Build)
Includes component smoke tests, rubric formatting assertions, and strict TypeScript compilation:

```bash
cd frontend
# Run unit & router tests
npm run test

# Type-check and verify production build
npm run build
```

---

## REST API Specification

All API endpoints are prefixed with `/api/`. Standard error responses adhere to a consistent error envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content does not meet minimum requirements.",
    "details": {
      "classes_responsibilities": ["This section must contain at least 60 characters."]
    }
  }
}
```

### Endpoints Table

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/api/health/` | System health & database liveness check | `200` |
| `GET` | `/api/problems/` | List all 5 problems with metadata & tags | `200` |
| `GET` | `/api/problems/<slug>/` | Get complete problem brief, requirements & edge cases | `200`, `404` |
| `GET` | `/api/attempts/` | Filter attempts by `?problem=<slug>` or `?status=<status>` | `200` |
| `POST` | `/api/attempts/` | Create a new attempt draft (`problem_slug`, optional `idempotency_key`) | `201`, `200` (dedup) |
| `GET` | `/api/attempts/<uuid>/` | Retrieve full attempt details and evaluation | `200`, `404` |
| `PATCH` | `/api/attempts/<uuid>/` | Autosave draft attempt sections | `200`, `409` (if not draft) |
| `POST` | `/api/attempts/<uuid>/submit/` | Validate & trigger asynchronous evaluation | `202`, `400`, `409` |
| `GET` | `/api/attempts/<uuid>/status/` | Lightweight polling endpoint for attempt & evaluation state | `200`, `404` |
| `POST` | `/api/attempts/<uuid>/retry/` | Clone existing attempt into a fresh draft (history preserved) | `201`, `404` |
| `POST` | `/api/attempts/<uuid>/re-evaluate/` | Re-trigger evaluation on a failed attempt | `202`, `409` |

---

## Quality & Pre-Launch Checklist

The platform was built and audited against a comprehensive 40-point verification checklist:
- **20/20 Website Quality**: No horizontal scroll on any viewport (down to 360px), accessible mobile navigation menu, SVG favicon, distinct route titles and meta descriptions, custom 404 handler, current copyright year, zero dead buttons or links, clear CTAs, explicit accessible error & success notifications.
- **20/20 Pre-Launch Security & SEO**: Fully functional Privacy Policy (`/privacy`) and Terms of Service (`/terms`), zero frontend-exposed secrets, production HTTPS redirect configurations, valid `sitemap.xml` and `robots.txt`, Open Graph social card preview, bot honeypot protection on editors, and strict two-tier (client + server) validation.

---

## Known Limitations & Roadmap

1. **In-Memory Threading for Async Evaluation**: Evaluations run inside a background daemon thread with frontend polling. This eliminates external broker dependencies for local development. For large multi-tenant production scale, the next step is a Celery/Redis queue or transactional outbox worker.
2. **SQLite Local Concurrency**: While SQLite WAL mode is configured with retry handlers, SQLite is intended for single-developer local evaluation. Production environments should use PostgreSQL (as configured in `docker-compose.yml`).
3. **No Authentication Layer**: To prioritize the core LLD practice loop within the 2-day timeframe, user authentication was intentionally omitted. Attempt history is stored globally in the local instance.

---

## AI Usage Disclosure

In compliance with the assignment instructions, an explicit disclosure of AI collaboration is documented in [`AI_USAGE.md`](AI_USAGE.md). It outlines 5 meaningful design decisions where AI assistance was evaluated, critically modified, or rejected to protect domain clarity and project scope.

---

## License & Credits

Built with precision for the **CipherSchools Engineering Assignment (September 2026)**.
Repository: [https://github.com/akcodes-py/LLD--practice-Platform](https://github.com/akcodes-py/LLD--practice-Platform)
