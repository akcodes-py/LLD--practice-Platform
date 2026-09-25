import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ScoreBar, StatusBadge } from "../components/chrome";
import { criterionLabel } from "../lib/api";

describe("chrome primitives", () => {
  it("renders each attempt status distinctly", () => {
    const { rerender } = render(<StatusBadge status="draft" />);
    expect(screen.getByText("draft")).toBeInTheDocument();
    rerender(<StatusBadge status="failed" />);
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("exposes score to assistive tech", () => {
    render(<ScoreBar score={82.5} />);
    expect(screen.getByRole("img", { name: /82.5 out of 100/ })).toBeInTheDocument();
  });
});

describe("rubric labels", () => {
  it("covers all 8 criteria without leaking raw keys", () => {
    for (const key of [
      "requirement_understanding",
      "class_responsibilities",
      "coupling",
      "encapsulation",
      "abstraction",
      "extensibility",
      "edge_cases",
      "explanation",
    ]) {
      expect(criterionLabel(key)).not.toBe(key);
    }
  });
});

describe("routing smoke", () => {
  it("memory router mounts", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <p>ok</p>
      </MemoryRouter>
    );
    expect(screen.getByText("ok")).toBeInTheDocument();
  });
});
