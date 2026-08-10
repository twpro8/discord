import { render, screen } from "@testing-library/react";

import { Avatar } from "../avatar";

describe("Avatar", () => {
  it("updates the image src when the URL changes", () => {
    const { rerender } = render(
      <Avatar name="Ada" src="https://cdn.example.com/avatar-old.png" />,
    );
    const image = screen.getByRole("img", { name: "Ada" });
    expect(image).toHaveAttribute(
      "src",
      "https://cdn.example.com/avatar-old.png",
    );

    rerender(
      <Avatar name="Ada" src="https://cdn.example.com/avatar-new.png" />,
    );

    expect(screen.getByRole("img", { name: "Ada" })).toHaveAttribute(
      "src",
      "https://cdn.example.com/avatar-new.png",
    );
  });
});
