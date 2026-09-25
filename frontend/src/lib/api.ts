export interface ProblemSummary {
  slug: string;
  title: string;
  summary: string;
  difficulty: string;
  tags: string[];
  estimated_minutes: number;
}

export interface ProblemDetail extends ProblemSummary {
  description: string;
  functional_requirements: string[];
  constraints: string[];
  design_considerations: string[];
  edge_cases: string[];
}

export interface RubricItem {
  criterion: string;
  score: number;
  evidence: string;
  concern: string;
  suggestion: string;
  confidence: number;
}

export interface Evaluation {
  state: "submitted" | "evaluating" | "completed" | "failed";
  provider: "rule_based" | "llm";
  total_score: number | null;
  rubric_results: RubricItem[];
  overall_feedback: string;
  strengths: string[];
  improvements: string[];
  error: string;
  created_at?: string;
  completed_at?: string | null;
}

export interface Attempt {
  id: string;
  problem: string;
  problem_slug: string;
  problem_title: string;
  status: "draft" | "submitted" | "evaluating" | "completed" | "failed";
  requirements_assumptions: string;
  classes_responsibilities: string;
  relationships_interfaces: string;
  workflows: string;
  tradeoffs: string;
  edge_cases: string;
  created_at: string;
  updated_at: string;
  submitted_at: string | null;
  evaluation?: Evaluation | null;
}

export interface ApiError {
  error: { code: string; message: string; details: Record<string, string[]> };
}

const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "") || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = data as ApiError;
    throw Object.assign(new Error(err?.error?.message ?? `Request failed (${res.status})`), {
      code: err?.error?.code ?? "unknown",
      details: err?.error?.details ?? {},
      status: res.status,
    });
  }
  return data as T;
}

export const api = {
  problems: () => request<ProblemSummary[]>("/problems/"),
  problem: (slug: string) => request<ProblemDetail>(`/problems/${slug}/`),
  attempts: (problem?: string) =>
    request<Attempt[]>(`/attempts/${problem ? `?problem=${encodeURIComponent(problem)}` : ""}`),
  attempt: (id: string) => request<Attempt>(`/attempts/${id}/`),
  pollAttemptStatus: (id: string) => request<Attempt>(`/attempts/${id}/status/`),
  createAttempt: (problem_slug: string) =>
    request<Attempt>("/attempts/", {
      method: "POST",
      body: JSON.stringify({ problem_slug, idempotency_key: crypto.randomUUID() }),
    }),
  updateAttempt: (id: string, patch: Partial<Attempt>) =>
    request<Attempt>(`/attempts/${id}/`, { method: "PATCH", body: JSON.stringify(patch) }),
  submitAttempt: (id: string) =>
    request<Attempt>(`/attempts/${id}/submit/`, { method: "POST", body: JSON.stringify({}) }),
  retryAttempt: (id: string) =>
    request<Attempt>(`/attempts/${id}/retry/`, { method: "POST", body: JSON.stringify({}) }),
  reEvaluate: (id: string) =>
    request<Attempt>(`/attempts/${id}/re-evaluate/`, { method: "POST", body: JSON.stringify({}) }),
};

export type AttemptPatch = Partial<Attempt>;

export function criterionLabel(key: string): string {
  const labels: Record<string, string> = {
    requirement_understanding: "Requirement understanding",
    class_responsibilities: "Class responsibilities & cohesion",
    coupling: "Coupling & dependencies",
    encapsulation: "Encapsulation & interfaces",
    abstraction: "Abstraction & patterns",
    extensibility: "Extensibility & trade-offs",
    edge_cases: "Edge cases & testability",
    explanation: "Quality of explanation",
  };
  return labels[key] ?? key;
}
