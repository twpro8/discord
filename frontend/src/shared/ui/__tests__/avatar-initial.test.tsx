import { render, screen } from "@testing-library/react";

import { AvatarInitial } from "../avatar-initial";

describe("AvatarInitial", () => {
  it("renders the first letter of the username, uppercased", () => {
    render(<AvatarInitial username="alice" />);
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("renders no status dot when status is omitted", () => {
    render(<AvatarInitial username="alice" />);
    expect(screen.queryByText("Online")).not.toBeInTheDocument();
    expect(screen.queryByText("Away")).not.toBeInTheDocument();
    expect(screen.queryByText("Offline")).not.toBeInTheDocument();
  });

  it("renders no status dot for offline — it's the default, unconnected state", () => {
    render(<AvatarInitial username="alice" status="offline" />);
    expect(screen.queryByText("Online")).not.toBeInTheDocument();
    expect(screen.queryByText("Away")).not.toBeInTheDocument();
    expect(screen.queryByText("Offline")).not.toBeInTheDocument();
  });

  it.each([
    ["online", "Online"],
    ["away", "Away"],
  ] as const)(
    "pairs the %s status with visually-hidden text, not color alone",
    (status, label) => {
      render(<AvatarInitial username="alice" status={status} />);
      const hiddenText = screen.getByText(label);
      expect(hiddenText).toBeInTheDocument();
      expect(hiddenText).toHaveClass("sr-only");
    },
  );
});
