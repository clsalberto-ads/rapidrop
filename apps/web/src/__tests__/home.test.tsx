import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Home", () => {
  it("renders the RapiDrop heading", () => {
    render(<Home />);
    expect(screen.getByText("RapiDrop")).toBeInTheDocument();
  });
});
