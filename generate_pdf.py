"""Generate comprehensive, publication-quality DESIGN.pdf for the LLD Practice Platform."""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Palette
PRIMARY = colors.HexColor("#0F172A")       # Deep slate navy
SECONDARY = colors.HexColor("#1E293B")     # Dark slate
ACCENT = colors.HexColor("#E07D18")        # Brand orange (CipherSchools brand)
ACCENT_LIGHT = colors.HexColor("#FFF7ED")  # Soft orange tint
TEXT_MAIN = colors.HexColor("#334155")     # Slate 700
TEXT_MUTED = colors.HexColor("#64748B")    # Slate 500
BORDER_COLOR = colors.HexColor("#CBD5E1")  # Slate 300
BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
SUCCESS_COLOR = colors.HexColor("#15803D") # Emerald 700
BLUE_CARD = colors.HexColor("#EFF6FF")      # Light blue


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#94A3B8"))

        # Skip running header/footer on title cover (Page 1)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 800, "LLD Practice Platform — System Design & Architecture Specification")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 792, 541, 792)

            # Footer
            self.line(54, 45, 541, 45)
            self.drawString(54, 32, "CipherSchools 2-Day Engineering Assignment | https://github.com/akcodes-py/LLD--practice-Platform")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(541, 32, page_text)

        self.restoreState()


def create_design_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_MAIN
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=SECONDARY
    )

    story = []

    # ================= COVER / TITLE SECTION =================
    story.append(Paragraph("LLD Practice Platform", title_style))
    story.append(Paragraph("System Architecture, Domain Design & Technical Specification", subtitle_style))

    # Meta card table
    meta_data = [
        [
            Paragraph("<b>Target Assignment:</b> CipherSchools 2-Day Engineering Challenge", table_cell_style),
            Paragraph("<b>Date:</b> September 2026", table_cell_style)
        ],
        [
            Paragraph("<b>Candidate / Author:</b> Rahul (akcodes-py)", table_cell_style),
            Paragraph("<b>Version:</b> 1.0 (Production Candidate)", table_cell_style)
        ],
        [
            Paragraph("<b>Repository:</b> github.com/akcodes-py/LLD--practice-Platform", table_cell_style),
            Paragraph("<b>Tech Stack:</b> React + TS + Django + PostgreSQL", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[240, 247])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ================= 1. EXECUTIVE SUMMARY & PROBLEM STATEMENT =================
    story.append(Paragraph("1. Executive Summary & Problem Framing", h1_style))
    story.append(Paragraph(
        "Low-Level Design (LLD) practice is critically underserved by existing prep resources. While algorithms have deterministic judges (LeetCode) and courses offer passive video walkthroughs, LLD practice suffers from four core cognitive hurdles:",
        body_style
    ))
    story.append(Paragraph("• <b>No Single Ground Truth:</b> In LLD, two competent designs (e.g. central coordinator vs distributed actors) can look entirely different. Learners get paralyzed asking <i>'Which answer is correct?'</i> rather than evaluating trade-offs.", bullet_style))
    story.append(Paragraph("• <b>Vague, Unactionable Feedback:</b> Human feedback is slow or absent; naive AI prompts drift wildly without fixed rubrics, often praising bad designs or hallucinating arbitrary scores.", bullet_style))
    story.append(Paragraph("• <b>Lost Iteration Evidence:</b> Designs live in ephemeral whiteboards or notebooks. Progress is invisible because attempts are never preserved across a learning loop.", bullet_style))
    story.append(Paragraph("• <b>Ambiguous Submission Bar:</b> Learners rarely know what a complete design specification requires (requirements mapping, class contracts, relationships, edge cases, trade-offs).", bullet_style))
    story.append(Paragraph(
        "<b>Core Product Goal:</b> Build the smallest submission format that reliably proves design thinking, evaluated by the smallest feedback engine that truly teaches.",
        body_style
    ))

    # ================= 2. MVP SCOPE & USER JOURNEY =================
    story.append(Paragraph("2. MVP Scope & End-to-End User Journey", h1_style))
    story.append(Paragraph(
        "The platform delivers an unhindered practice loop without bloatware (no LMS, payments, or mandatory auth):",
        body_style
    ))

    journey_diagram = (
        "<b>Catalog Selection</b> (/problems) ➔ <b>Problem Brief</b> (/problems/:slug)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;➔ <b>Drafting Attempt</b> (/attempts/:id with autosave & validation)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➔ <b>Async Submit</b> (202 Accepted + background worker)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➔ <b>Rubric Feedback Review</b> (/attempts/:id/review)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;➔ <b>Attempt History</b> (/history) ➔ <b>One-Click Retry</b> (clones to new draft)"
    )
    journey_table = Table([[Paragraph(journey_diagram, code_style)]], colWidths=[487])
    journey_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDBA74")),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(journey_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>5 Included Interview-Grade Problems:</b>", h2_style))
    problems_data = [
        [
            Paragraph("<b>Problem</b>", table_header_style),
            Paragraph("<b>Key Design Complexity & Architectural Patterns</b>", table_header_style),
            Paragraph("<b>Est. Time</b>", table_header_style)
        ],
        [
            Paragraph("<b>Parking Lot</b>", table_cell_style),
            Paragraph("Multi-floor vehicle sizing, dynamic spot allocation (Strategy pattern), barrier gates, concurrency locks.", table_cell_style),
            Paragraph("45 min", table_cell_style)
        ],
        [
            Paragraph("<b>Elevator System</b>", table_cell_style),
            Paragraph("Dispatcher algorithms (LOOK/SCAN), internal/external requests, motion state machine, emergency handling.", table_cell_style),
            Paragraph("45 min", table_cell_style)
        ],
        [
            Paragraph("<b>Vending Machine</b>", table_cell_style),
            Paragraph("Explicit State Machine (Idle, HasMoney, Dispensing, SoldOut), coin/cash validation, inventory locks.", table_cell_style),
            Paragraph("30 min", table_cell_style)
        ],
        [
            Paragraph("<b>Library Management</b>", table_cell_style),
            Paragraph("Catalog indexing, fine computation rules (Strategy), hold/reservation queue, borrowing limits.", table_cell_style),
            Paragraph("30 min", table_cell_style)
        ],
        [
            Paragraph("<b>Food Ordering System</b>", table_cell_style),
            Paragraph("Restaurant menus, multi-item cart lifecycle, payment gateway integration (Adapter), live order tracking.", table_cell_style),
            Paragraph("45 min", table_cell_style)
        ]
    ]
    prob_table = Table(problems_data, colWidths=[100, 335, 52])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(prob_table)

    story.append(PageBreak())

    # ================= 3. SYSTEM ARCHITECTURE & DOMAIN MODEL =================
    story.append(Paragraph("3. System Architecture & Domain Model", h1_style))
    story.append(Paragraph(
        "The architecture is structured as a resilient, modular monolith. The system enforces strict separation of concerns: views remain thin HTTP translation layers, all validation and state transitions live in <code>services.py</code>, and evaluation engines comply with a shared result schema.",
        body_style
    ))

    arch_diagram = (
        "<b>Frontend (React 18 SPA)</b><br/>"
        "  ├── Pages: Home, ProblemList, ProblemDetail, AttemptEditor, AttemptReview, History<br/>"
        "  └── Lib: REST API Client (Fetch + Poller), Design Tokens, Metadata Hooks<br/>"
        "           │<br/>"
        "           ▼ REST API (JSON Over HTTP / Reverse Proxy)<br/>"
        "<b>Backend (Django 5 + Django REST Framework)</b><br/>"
        "  ├── <b>HTTP Layer (practice/views.py):</b> Thin endpoints, standard error envelope<br/>"
        "  ├── <b>Domain Layer (practice/services.py):</b> Content validation, async runner, retry/clone<br/>"
        "  ├── <b>Data Entities (practice/models.py):</b> Problem, Attempt, Evaluation<br/>"
        "  └── <b>Evaluators (practice/evaluators/):</b><br/>"
        "        ├── base.py       - Evaluation result contract & schema validation<br/>"
        "        ├── rule_based.py - Deterministic heuristic scorer + citation extractor<br/>"
        "        └── llm.py        - Optional OpenAI-compatible schema-constrained evaluator<br/>"
        "           │<br/>"
        "           ▼ Django ORM (WAL Journaling + Concurrency Retry Handlers)<br/>"
        "<b>Storage:</b> SQLite (Local Zero-Config) / PostgreSQL 16 (Docker Production)"
    )
    arch_table = Table([[Paragraph(arch_diagram, code_style)]], colWidths=[487])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Domain Entities & Class Responsibilities:</b>", h2_style))
    classes_data = [
        [
            Paragraph("<b>Entity / Module</b>", table_header_style),
            Paragraph("<b>Single Responsibility</b>", table_header_style),
            Paragraph("<b>Invariants & Dependencies</b>", table_header_style)
        ],
        [
            Paragraph("<b>Problem</b>", table_cell_style),
            Paragraph("Immutable specification prompt (requirements, constraints, edge cases, suggested time).", table_cell_style),
            Paragraph("Zero dependencies. Seeded idempotently via <code>seed_problems</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>Attempt</b>", table_cell_style),
            Paragraph("Encapsulates the 6 design sections, learner status (<code>draft, submitted, evaluating, completed, failed</code>), and timestamps.", table_cell_style),
            Paragraph("Belongs to a <code>Problem</code>. Edits permitted only when in <code>draft</code> state.", table_cell_style)
        ],
        [
            Paragraph("<b>Evaluation</b>", table_cell_style),
            Paragraph("Stores immutable assessment payload (provider, total score, 8 rubric criteria items, overall feedback, cited evidence).", table_cell_style),
            Paragraph("1-to-1 relationship with <code>Attempt</code>. Conforms strictly to <code>base.py</code> contract.", table_cell_style)
        ],
        [
            Paragraph("<b>services.py</b>", table_cell_style),
            Paragraph("Orchestrates attempt creation, patch autosaving, synchronous persistence, async worker dispatch, and retry cloning.", table_cell_style),
            Paragraph("Coordinates models and evaluators. Ensures DB commit precedes thread spawn.", table_cell_style)
        ],
        [
            Paragraph("<b>evaluators/base.py</b>", table_cell_style),
            Paragraph("Defines the formal evaluation contract (<code>validate_result</code>) ensuring provider swappability.", table_cell_style),
            Paragraph("No external dependencies. Validates types, bounds (0-10), and mandatory quotes.", table_cell_style)
        ]
    ]
    classes_table = Table(classes_data, colWidths=[100, 217, 170])
    classes_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(classes_table)

    story.append(Spacer(1, 10))

    # ================= 4. SUBMISSION & EVALUATION ENGINE =================
    story.append(Paragraph("4. Submission Format & Evaluation Engine", h1_style))
    story.append(Paragraph(
        "<b>Why Structured Text over Code or Diagrams?</b><br/>"
        "Full code editors necessitate language runtimes and compiler sandboxes; diagram canvases burden learners with UI manipulation. Neither isolates architectural judgment. The six-section structured text format requires the candidate to explicitly communicate responsibilities, interface boundaries, and trade-offs—the exact signal evaluated in LLD interviews.",
        body_style
    ))

    story.append(Paragraph("<b>The 8-Criterion Explainable Rubric:</b>", h2_style))
    rubric_data = [
        [
            Paragraph("<b>#</b>", table_header_style),
            Paragraph("<b>Rubric Criterion</b>", table_header_style),
            Paragraph("<b>What Is Evaluated & Evidence Extracted</b>", table_header_style)
        ],
        [
            Paragraph("1", table_cell_style),
            Paragraph("Requirement Understanding", table_cell_style),
            Paragraph("Mapping of functional requirements into domain entities; clarity of operational assumptions.", table_cell_style)
        ],
        [
            Paragraph("2", table_cell_style),
            Paragraph("Responsibilities & Cohesion", table_cell_style),
            Paragraph("Single Responsibility Principle (SRP); avoidance of monolithic 'God' classes.", table_cell_style)
        ],
        [
            Paragraph("3", table_cell_style),
            Paragraph("Coupling & Class Relationships", table_cell_style),
            Paragraph("Dependency direction, composition over inheritance, avoidance of tight cyclic couplings.", table_cell_style)
        ],
        [
            Paragraph("4", table_cell_style),
            Paragraph("Encapsulation & Interfaces", table_cell_style),
            Paragraph("Public contracts vs private state; adherence to Interface Segregation & Dependency Inversion.", table_cell_style)
        ],
        [
            Paragraph("5", table_cell_style),
            Paragraph("Abstraction & Patterns", table_cell_style),
            Paragraph("Judicious use of design patterns (Strategy, State, Observer, Factory) without over-engineering.", table_cell_style)
        ],
        [
            Paragraph("6", table_cell_style),
            Paragraph("Extensibility & Trade-offs", table_cell_style),
            Paragraph("Open-Closed Principle (OCP); clear justification for chosen architectural trade-offs.", table_cell_style)
        ],
        [
            Paragraph("7", table_cell_style),
            Paragraph("Edge Cases & Testability", table_cell_style),
            Paragraph("Handling of concurrency, hardware/network failure, capacity limits, and unit test strategy.", table_cell_style)
        ],
        [
            Paragraph("8", table_cell_style),
            Paragraph("Explanation Quality", table_cell_style),
            Paragraph("Communication clarity, coherent workflow execution traces, and structured reasoning.", table_cell_style)
        ]
    ]
    rubric_table = Table(rubric_data, colWidths=[20, 160, 307])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(rubric_table)

    story.append(PageBreak())

    # ================= 5. DETERMINISTIC VS JUDGMENT & ERROR RESILIENCE =================
    story.append(Paragraph("5. Deterministic vs. Judgment Split & Resilience", h1_style))
    story.append(Paragraph(
        "A foundational principle of this architecture is separating deterministic boundaries from subjective judgment:",
        body_style
    ))
    story.append(Paragraph("• <b>Deterministic Pipeline:</b> Input validation (min 60 chars per section), honeypot spam detection, idempotency key deduplication, and lifecycle state enforcement are 100% deterministic.", bullet_style))
    story.append(Paragraph("• <b>Rule-Based Evaluator (Default):</b> Executes completely offline in <10ms. Analyzes structural breadth, vocabulary, pattern markers, and quotes candidate text. Always labelled truthfully as <i>'Rule-based review'</i> in the UI.", bullet_style))
    story.append(Paragraph("• <b>LLM Evaluator (Optional):</b> Activated only via <code>LLM_ENABLED=1</code>. Bound by strict system prompts, JSON output schemas, and 20s timeouts. If the LLM produces invalid JSON or fails, the attempt transitions to a visible <code>failed</code> state with an instant <i>Re-evaluate</i> action.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>State Machine & Failure Transitions:</b>", h2_style))

    state_diagram = (
        "<b>[DRAFT]</b> ──(Submit Request)──▶ <b>Persist synchronously to DB</b><br/>"
        "                                           │<br/>"
        "                                           ▼<br/>"
        "                             Spawn Daemon Evaluation Thread<br/>"
        "                                           │<br/>"
        "                                    <b>[EVALUATING]</b> (Client polls every 1.5s)<br/>"
        "                                   ╱              ╲<br/>"
        "                  (Evaluator Success)            (Timeout / Parser Error)<br/>"
        "                          ▼                                 ▼<br/>"
        "                    <b>[COMPLETED]</b>                       <b>[FAILED]</b><br/>"
        "                          │                                 │<br/>"
        "                          ▼                                 ▼<br/>"
        "                 <b>One-Click Retry</b>                  <b>Re-Evaluate Action</b><br/>"
        "            (Clones into fresh Draft)           (Re-triggers async worker)"
    )
    state_table = Table([[Paragraph(state_diagram, code_style)]], colWidths=[487])
    state_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(state_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Crash Safety Guarantee:</b>", h2_style))
    story.append(Paragraph(
        "In <code>services.py</code>, the submission content is atomically written to disk and status set to <code>evaluating</code> <i>before</i> the thread is launched. Even if the backend process suffers a hardware restart or crash mid-evaluation, the user's design is never lost. On boot, the user sees the attempt and can trigger re-evaluation.",
        body_style
    ))

    # ================= 6. REST API & CONTRACTS =================
    story.append(Paragraph("6. REST API Specification & Error Handling", h1_style))
    story.append(Paragraph(
        "All endpoints reside under <code>/api/</code>. Standard errors share a uniform envelope: <code>{\"error\": {\"code\", \"message\", \"details\"}}</code>.",
        body_style
    ))

    api_data = [
        [
            Paragraph("<b>Method & Route</b>", table_header_style),
            Paragraph("<b>Description & Request Payload</b>", table_header_style),
            Paragraph("<b>Status Codes</b>", table_header_style)
        ],
        [
            Paragraph("<code>GET /api/health/</code>", table_cell_style),
            Paragraph("Database liveness and container health check.", table_cell_style),
            Paragraph("<code>200 OK</code>", table_cell_style)
        ],
        [
            Paragraph("<code>GET /api/problems/</code>", table_cell_style),
            Paragraph("Lists all 5 problems with metadata, difficulty, tags, and summary.", table_cell_style),
            Paragraph("<code>200 OK</code>", table_cell_style)
        ],
        [
            Paragraph("<code>GET /api/problems/&lt;slug&gt;/</code>", table_cell_style),
            Paragraph("Full brief: functional requirements, constraints, edge cases.", table_cell_style),
            Paragraph("<code>200, 404</code>", table_cell_style)
        ],
        [
            Paragraph("<code>POST /api/attempts/</code>", table_cell_style),
            Paragraph("Creates draft attempt. Accepts <code>problem_slug</code> & <code>idempotency_key</code>.", table_cell_style),
            Paragraph("<code>201, 200 (dedup)</code>", table_cell_style)
        ],
        [
            Paragraph("<code>PATCH /api/attempts/&lt;id&gt;/</code>", table_cell_style),
            Paragraph("Autosaves draft sections. Enforces draft-only lock.", table_cell_style),
            Paragraph("<code>200, 409 Conflict</code>", table_cell_style)
        ],
        [
            Paragraph("<code>POST /api/attempts/&lt;id&gt;/submit/</code>", table_cell_style),
            Paragraph("Validates fields, commits row, dispatches background evaluation.", table_cell_style),
            Paragraph("<code>202 Accepted, 400</code>", table_cell_style)
        ],
        [
            Paragraph("<code>GET /api/attempts/&lt;id&gt;/status/</code>", table_cell_style),
            Paragraph("Lightweight poller returning status and evaluation result if complete.", table_cell_style),
            Paragraph("<code>200 OK, 404</code>", table_cell_style)
        ],
        [
            Paragraph("<code>POST /api/attempts/&lt;id&gt;/retry/</code>", table_cell_style),
            Paragraph("Clones content into fresh draft (history preserved).", table_cell_style),
            Paragraph("<code>201 Created</code>", table_cell_style)
        ],
        [
            Paragraph("<code>POST /api/attempts/&lt;id&gt;/re-evaluate/</code>", table_cell_style),
            Paragraph("Re-runs evaluator on failed attempts.", table_cell_style),
            Paragraph("<code>202 Accepted, 409</code>", table_cell_style)
        ]
    ]
    api_table = Table(api_data, colWidths=[140, 267, 80])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(api_table)

    story.append(PageBreak())

    # ================= 7. EXTENSIBILITY CHANGE TESTS & TRADE-OFFS =================
    story.append(Paragraph("7. Architectural Change Tests & Trade-offs", h1_style))
    story.append(Paragraph(
        "A great design is evaluated by how easily it accommodates future change without rewriting core abstractions:",
        body_style
    ))

    story.append(Paragraph("<b>Change Test A: Adding a Diagram Submission Format</b>", h2_style))
    story.append(Paragraph(
        "• <i>Requirement:</i> Support Mermaid.js or visual graph node/edge JSON submissions.<br/>"
        "• <i>Impact on Current Design:</i> Add a nullable <code>diagram_data = JSONField()</code> to <code>Attempt</code>. The core state lifecycle (draft ➔ submit ➔ evaluate ➔ retry) and problem catalog remain untouched. An adapter extracts class names and relationships from diagram nodes to feed the existing rubric contract.",
        body_style
    ))

    story.append(Paragraph("<b>Change Test B: Adding Human Mentorship Review</b>", h2_style))
    story.append(Paragraph(
        "• <i>Requirement:</i> Allow human senior engineers to grade attempts alongside automated review.<br/>"
        "• <i>Impact on Current Design:</i> The <code>Evaluation</code> entity already accepts arbitrary <code>provider</code> keys (e.g. <code>'human_mentor'</code>). A mentor review UI simply posts to an internal evaluation endpoint with the identical 8-rubric JSON schema. The frontend review component renders it transparently.",
        body_style
    ))

    story.append(Paragraph("<b>Scalability Trade-off Analysis:</b>", h2_style))
    tradeoff_data = [
        [
            Paragraph("<b>Dimension</b>", table_header_style),
            Paragraph("<b>Choice in MVP</b>", table_header_style),
            Paragraph("<b>Production Scale Step (Roadmap)</b>", table_header_style)
        ],
        [
            Paragraph("<b>Async Worker</b>", table_cell_style),
            Paragraph("Python daemon thread + DB pooling. Zero broker infra for local dev.", table_cell_style),
            Paragraph("Persistent <code>EvaluationJob</code> table polled by dedicated worker, or Celery + Redis.", table_cell_style)
        ],
        [
            Paragraph("<b>Database</b>", table_cell_style),
            Paragraph("SQLite with WAL + busy timeout (zero-setup dev); Postgres in Docker.", table_cell_style),
            Paragraph("Managed PostgreSQL with read-replicas for catalog and history queries.", table_cell_style)
        ],
        [
            Paragraph("<b>Authentication</b>", table_cell_style),
            Paragraph("Omitted for 2-day MVP to focus 100% on the core LLD practice loop.", table_cell_style),
            Paragraph("OAuth2 / Session auth partitioning <code>Attempt</code> records by <code>user_id</code>.", table_cell_style)
        ]
    ]
    tradeoff_table = Table(tradeoff_data, colWidths=[90, 197, 200])
    tradeoff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tradeoff_table)

    story.append(Spacer(1, 10))

    # ================= 8. VERIFICATION & QUALITY AUDIT =================
    story.append(Paragraph("8. Quality & Pre-Launch Verification Summary", h1_style))
    story.append(Paragraph(
        "Audited against the mandatory 40-point verification checklist (see <code>docs/CHECKLIST.md</code>):",
        body_style
    ))
    story.append(Paragraph("• <b>Website Quality (20/20):</b> Responsive layouts tested down to 360px (zero horizontal scroll), working mobile drawer, SVG favicon, per-route document titles and meta descriptions, accessible focus rings, current copyright year, custom 404 handler, and zero broken links.", bullet_style))
    story.append(Paragraph("• <b>Pre-Launch & Security (20/20):</b> Functional Privacy Policy and Terms of Service, secrets isolated strictly to backend environment variables (never in frontend code), Open Graph preview cards, valid robots.txt and sitemap.xml, and honeypot protection.", bullet_style))
    story.append(Paragraph("• <b>Test Suite Coverage:</b> 13 backend tests (Pytest) exercising full API journeys, input validation, duplicate rejections, and evaluator contracts; 4 frontend tests (Vitest) validating rubric formatting and router smoke.", bullet_style))

    story.append(Spacer(1, 14))

    # Callout Box
    summary_box = [
        [
            Paragraph(
                "<b>Architectural Takeaway:</b><br/>"
                "The LLD Practice Platform demonstrates that effective domain design is not about piling up distributed tools or decorative microservices, but about crafting cohesive, single-responsibility domain entities, clear interface contracts, honest evaluation feedback, and crash-resilient user loops.",
                callout_style
            )
        ]
    ]
    summary_table = Table(summary_box, colWidths=[487])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(summary_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "DESIGN.pdf"
    create_design_pdf(out)
