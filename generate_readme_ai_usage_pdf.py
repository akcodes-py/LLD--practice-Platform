"""Generate a single unified README_AND_AI_USAGE.pdf for Google Form submission."""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Palette
PRIMARY = colors.HexColor("#0F172A")       # Deep slate navy
SECONDARY = colors.HexColor("#1E293B")     # Dark slate
ACCENT = colors.HexColor("#E07D18")        # CipherSchools brand orange
ACCENT_LIGHT = colors.HexColor("#FFF7ED")  # Soft orange tint
TEXT_MAIN = colors.HexColor("#334155")     # Slate 700
TEXT_MUTED = colors.HexColor("#64748B")    # Slate 500
BORDER_COLOR = colors.HexColor("#CBD5E1")  # Slate 300
BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
SUCCESS_COLOR = colors.HexColor("#15803D") # Emerald 700


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

        if self._pageNumber > 1:
            # Header
            self.drawString(54, 800, "LLD Practice Platform — README + AI_USAGE Report")
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.5)
            self.line(54, 792, 541, 792)

            # Footer
            self.line(54, 45, 541, 45)
            self.drawString(54, 32, "CipherSchools Engineering Assignment | https://github.com/akcodes-py/LLD--practice-Platform")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(541, 32, page_text)

        self.restoreState()


def build_unified_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=ACCENT,
        spaceAfter=12
    )

    part_header_style = ParagraphStyle(
        "PartHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.white,
        spaceAfter=0
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_MAIN,
        spaceAfter=5
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
        leading=10.5,
        textColor=PRIMARY
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=TEXT_MAIN
    )

    ai_decision_title = ParagraphStyle(
        "AIDecisionTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    story = []

    # ================= COVER / TITLE SECTION =================
    story.append(Paragraph("LLD Practice Platform", title_style))
    story.append(Paragraph("Project README & AI Usage Report (Combined Submission Document)", subtitle_style))

    # Meta card table
    meta_data = [
        [
            Paragraph("<b>Hiring Assignment:</b> CipherSchools 2-Day Engineering Challenge", table_cell_style),
            Paragraph("<b>Date:</b> September 2026", table_cell_style)
        ],
        [
            Paragraph("<b>Candidate / Author:</b> Rahul (akcodes-py)", table_cell_style),
            Paragraph("<b>Document Purpose:</b> Single Upload for Google Form", table_cell_style)
        ],
        [
            Paragraph("<b>Repository:</b> https://github.com/akcodes-py/LLD--practice-Platform", table_cell_style),
            Paragraph("<b>Core Stack:</b> React 18, TypeScript, Django 5, DRF, PostgreSQL", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[240, 247])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # ================= PART 1: PROJECT README =================
    part1_bar = Table([[Paragraph("PART 1 — PROJECT DOCUMENTATION & RUN GUIDE", part_header_style)]], colWidths=[487])
    part1_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(part1_bar)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. System Overview & The Practice Loop", h1_style))
    story.append(Paragraph(
        "A focused Low-Level Design (LLD) practice and automated evaluation platform built for the CipherSchools 2-Day Engineering Challenge. "
        "The platform enables candidates to practice interview-grade LLD problems in a continuous learning loop: "
        "<b>Choose Problem ➔ Formulate Structured Design ➔ Submit ➔ Receive Explainable Feedback ➔ Review History ➔ Retry & Improve</b>.",
        body_style
    ))

    story.append(Paragraph("<b>5 Interview-Grade Problems Catalog:</b>", h2_style))
    story.append(Paragraph("1. <b>Parking Lot:</b> Multi-floor spot sizing, Strategy pattern allocation, barrier gates, fee calculation.", bullet_style))
    story.append(Paragraph("2. <b>Elevator System:</b> Dispatching algorithms (LOOK/SCAN), internal/external floor calls, motion states.", bullet_style))
    story.append(Paragraph("3. <b>Vending Machine:</b> State Pattern lifecycle (Idle, HasMoney, Dispensing, SoldOut), coin verification.", bullet_style))
    story.append(Paragraph("4. <b>Library Management:</b> Book cataloging, hold queues, borrowing limits, fine calculation rules.", bullet_style))
    story.append(Paragraph("5. <b>Food Ordering System:</b> Menus, cart lifecycle, payment gateway adapter, order delivery states.", bullet_style))

    story.append(Paragraph("2. System Architecture & Tech Stack", h1_style))
    story.append(Paragraph(
        "Designed as a clean, cohesive modular monolith with strict separation of domain rules from HTTP handling:",
        body_style
    ))
    story.append(Paragraph("• <b>Frontend:</b> React 18 SPA + Vite + TypeScript + Tailwind CSS (responsive down to 360px).", bullet_style))
    story.append(Paragraph("• <b>Backend Monolith:</b> Django 5 + Django REST Framework; views are thin controllers; all validation, state transitions, and background evaluation threads reside in <code>services.py</code>.", bullet_style))
    story.append(Paragraph("• <b>Persistence:</b> SQLite (WAL mode + busy_timeout for local dev); PostgreSQL 16 for Docker Compose.", bullet_style))
    story.append(Paragraph("• <b>Async Evaluation:</b> Atomic DB persistence before thread launch ➔ submit returns 202 Accepted ➔ frontend polls <code>/status/</code> every 1.5s ➔ feedback displayed.", bullet_style))

    story.append(Paragraph("3. How to Run the Project (Step-by-Step)", h1_style))
    story.append(Paragraph("<b>Option A: Zero-Config Local Setup (Recommended)</b>", h2_style))

    setup_code = (
        "# 1. Terminal 1 — Backend (http://127.0.0.1:8000)\n"
        "cd backend\n"
        "pip install -r requirements.txt\n"
        "python manage.py migrate\n"
        "python manage.py seed_problems    # Populates the 5 problems idempotently\n"
        "python manage.py runserver\n\n"
        "# 2. Terminal 2 — Frontend (http://localhost:5173)\n"
        "cd frontend\n"
        "npm install\n"
        "npm run dev\n"
        "# Note: Vite dev server automatically proxies /api to Django. No CORS setup needed!"
    )
    setup_box = Table([[Paragraph(setup_code.replace("\n", "<br/>"), code_style)]], colWidths=[487])
    setup_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(setup_box)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Option B: Docker Compose</b>", h2_style))
    docker_code = "copy .env.example .env\ndocker compose up --build\n# Frontend live at http://localhost:8080 (SPA served via Nginx reverse proxy)"
    docker_box = Table([[Paragraph(docker_code.replace("\n", "<br/>"), code_style)]], colWidths=[487])
    docker_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(docker_box)
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. REST API Specification", h1_style))
    story.append(Paragraph("Standard API error envelope: <code>{\"error\": {\"code\", \"message\", \"details\"}}</code>.", body_style))

    api_data = [
        [Paragraph("<b>Method & Route</b>", table_header_style), Paragraph("<b>Functionality</b>", table_header_style), Paragraph("<b>Status Codes</b>", table_header_style)],
        [Paragraph("<code>GET /api/health/</code>", table_cell_style), Paragraph("System health & database connectivity check", table_cell_style), Paragraph("200 OK", table_cell_style)],
        [Paragraph("<code>GET /api/problems/</code>", table_cell_style), Paragraph("List 5 practice problems with summary & difficulty", table_cell_style), Paragraph("200 OK", table_cell_style)],
        [Paragraph("<code>GET /api/problems/&lt;slug&gt;/</code>", table_cell_style), Paragraph("Full brief (requirements, constraints, edge cases)", table_cell_style), Paragraph("200, 404", table_cell_style)],
        [Paragraph("<code>POST /api/attempts/</code>", table_cell_style), Paragraph("Create draft attempt (idempotency key supported)", table_cell_style), Paragraph("201, 200 (dedup)", table_cell_style)],
        [Paragraph("<code>PATCH /api/attempts/&lt;id&gt;/</code>", table_cell_style), Paragraph("Autosave draft sections (rejected if not draft)", table_cell_style), Paragraph("200, 409 Conflict", table_cell_style)],
        [Paragraph("<code>POST /api/attempts/&lt;id&gt;/submit/</code>", table_cell_style), Paragraph("Persists submission & starts async evaluation", table_cell_style), Paragraph("202 Accepted, 400", table_cell_style)],
        [Paragraph("<code>GET /api/attempts/&lt;id&gt;/status/</code>", table_cell_style), Paragraph("Polling endpoint for attempt lifecycle & results", table_cell_style), Paragraph("200 OK, 404", table_cell_style)],
        [Paragraph("<code>POST /api/attempts/&lt;id&gt;/retry/</code>", table_cell_style), Paragraph("Clones content into new draft (history preserved)", table_cell_style), Paragraph("201 Created", table_cell_style)],
        [Paragraph("<code>POST /api/attempts/&lt;id&gt;/re-evaluate/</code>", table_cell_style), Paragraph("Re-runs evaluator on failed evaluations", table_cell_style), Paragraph("202 Accepted, 409", table_cell_style)]
    ]
    api_table = Table(api_data, colWidths=[140, 267, 80])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Test Suite Verification", h1_style))
    story.append(Paragraph("• <b>Backend (Pytest):</b> <code>13 passed, 0 failures</code> covering full API journeys, section validation checks, duplicate prevention, failure recovery, and evaluator schema contracts.", bullet_style))
    story.append(Paragraph("• <b>Frontend (Vitest & TSC):</b> <code>4 passed, 0 failures</code> covering router smoke tests, status badges, rubric labels, and zero-error TypeScript build (<code>tsc --noEmit && vite build</code>).", bullet_style))

    story.append(Paragraph("6. Known Limitations & Production Roadmap", h1_style))
    story.append(Paragraph("• <b>Background Threading:</b> Local async evaluation runs via daemon threads. For multi-tenant scale, migrate to a persistent <code>EvaluationJob</code> table polled by dedicated workers, or Celery + Redis.", bullet_style))
    story.append(Paragraph("• <b>Authentication:</b> Intentionally omitted for the 2-day MVP to prioritize the core practice loop. All attempt history is local to the instance.", bullet_style))
    story.append(Paragraph("• <b>Concurrency:</b> Local dev uses SQLite WAL with retry handlers; production deployments use PostgreSQL.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(PageBreak())

    # ================= PART 2: AI_USAGE REPORT =================
    part2_bar = Table([[Paragraph("PART 2 — AI USAGE REPORT (AI_USAGE.md)", part_header_style)]], colWidths=[487])
    part2_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SECONDARY),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(part2_bar)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "In accordance with Section 6 of the assignment brief, AI assistance (Claude/ChatGPT-style tools) was actively utilized as a sounding board during system design and implementation. Below is the explicit report on <b>5 meaningful AI-assisted decisions</b>, documenting what the AI suggested, what was accepted or rejected, and the engineering rationale.",
        body_style
    ))

    # Decision 1
    story.append(Paragraph("Decision 1: Submission Format — Structured Text over Code / Diagram Editors", ai_decision_title))
    story.append(Paragraph("• <b>AI Suggested:</b> Support full code and diagram canvas uploads from day one to provide 'richer candidate evidence'.", bullet_style))
    story.append(Paragraph("• <b>Accepted in Part / Rejected in Full:</b> Chose a six-section structured text submission format only.", bullet_style))
    story.append(Paragraph("• <b>Engineering Rationale:</b> Code execution requires language compiler sandboxes and test runners; diagram editors add heavy canvas manipulation without increasing signal on design judgment. The assignment brief emphasizes the <i>smallest sufficient format</i>. Six structured text sections capture requirements, class responsibilities, interfaces, and trade-offs directly, which is what LLD interviews actually test.", bullet_style))

    # Decision 2
    story.append(Paragraph("Decision 2: Evaluation Contract — Rubric with Mandatory Quoted Evidence", ai_decision_title))
    story.append(Paragraph("• <b>AI Suggested:</b> Return an overall 0–100 score with free-text critique paragraphs.", bullet_style))
    story.append(Paragraph("• <b>Accepted with Critical Modifications:</b> Enforced an 8-criterion rubric where <code>evidence</code> (quoted directly from the submission) and <code>confidence</code> are strictly required fields.", bullet_style))
    story.append(Paragraph("• <b>Engineering Rationale:</b> Unconstrained scores drift between runs and offer vague advice. Forcing the evaluation contract to cite verbatim sentences from the learner's text guarantees actionable feedback and makes deterministic heuristics directly comparable with LLM responses.", bullet_style))

    # Decision 3
    story.append(Paragraph("Decision 3: Deterministic Rule-Based Default with Optional LLM (Not AI-First)", ai_decision_title))
    story.append(Paragraph("• <b>AI Suggested:</b> Call an external LLM API for every evaluation to give 'deeper qualitative critique'.", bullet_style))
    story.append(Paragraph("• <b>Rejected as Default, Accepted as Opt-In:</b> The default evaluator is a deterministic, rule-based heuristic engine working offline in <10ms, truthfully labelled as 'Rule-based review'. The LLM path is strictly opt-in via <code>LLM_ENABLED=1</code>.", bullet_style))
    story.append(Paragraph("• <b>Engineering Rationale:</b> Candidates and reviewers running the project locally have no API keys configured. Fabricating fake AI reviews is dishonest. The assignment rewards separating deterministic checks from judgment and gracefully handling provider failures.", bullet_style))

    story.append(Spacer(1, 4))

    # Decision 4
    story.append(Paragraph("Decision 4: Async Evaluation via Daemon Thread + Polling (Not a Distributed Broker)", ai_decision_title))
    story.append(Paragraph("• <b>AI Suggested:</b> Install Celery + Redis or RabbitMQ to build a 'production-ready distributed job queue'.", bullet_style))
    story.append(Paragraph("• <b>Accepted with Changes (Simplified):</b> Implemented async evaluation via Python daemon threads with DB persistence before thread launch, returning 202 Accepted, and frontend client polling every 1.5s.", bullet_style))
    story.append(Paragraph("• <b>Engineering Rationale:</b> Introducing Celery and Redis violates the assignment's explicit instruction: <i>'Keep this practical; do not turn the assignment into a distributed-systems project.'</i> The daemon thread achieves the exact same non-blocking UX with zero extra infrastructure. Database rows are committed before thread spawn, ensuring zero data loss if a thread crashes.", bullet_style))

    # Decision 5
    story.append(Paragraph("Decision 5: UI Restraint Over Dashboard Clichés", ai_decision_title))
    story.append(Paragraph("• <b>AI Suggested:</b> Include animated gradient hero sections, analytics stat cards, decorative charts, and community social tabs.", bullet_style))
    story.append(Paragraph("• <b>Rejected:</b> Built a focused, accessible light theme (CipherSchools orange <code>#E07D18</code>, slate typography, clear hierarchy) centered entirely on the practice and review loop.", bullet_style))
    story.append(Paragraph("• <b>Engineering Rationale:</b> The 40-point checklist prioritizes mobile readability (down to 360px), color contrast, and clarity over decorative noise. The interface emphasizes the problem brief, autosaving editor, score progress bars, and expandable feedback panels.", bullet_style))

    story.append(Spacer(1, 10))

    # Summary box
    summary_box = [
        [
            Paragraph(
                "<b>Submission Summary:</b><br/>"
                "This document consolidates the complete project documentation (README) and the AI Usage Disclosure (AI_USAGE.md) into a single verified submission file. "
                "All source code, database seed scripts, unit tests, Docker configurations, and architectural notes are version-controlled at:<br/>"
                "👉 <b>https://github.com/akcodes-py/LLD--practice-Platform</b>",
                table_cell_style
            )
        ]
    ]
    summary_table = Table(summary_box, colWidths=[487])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated unified PDF: {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "README_AND_AI_USAGE.pdf"
    build_unified_pdf(out)
