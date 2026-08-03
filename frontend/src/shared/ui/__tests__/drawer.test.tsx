import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { Drawer } from "../drawer";

function renderDrawer(open: boolean, onClose: () => void) {
  return render(
    <Drawer open={open} onClose={onClose} label="Friends">
      <p>panel content</p>
    </Drawer>,
  );
}

describe("Drawer", () => {
  it("renders children when open", () => {
    renderDrawer(true, vi.fn());
    expect(screen.getByText("panel content")).toBeInTheDocument();
  });

  it("does not render children when closed", () => {
    renderDrawer(false, vi.fn());
    expect(screen.queryByText("panel content")).not.toBeInTheDocument();
  });

  it("calls onClose when Escape is pressed", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    renderDrawer(true, onClose);
    await user.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalled();
  });

  it("calls onClose when the overlay is clicked", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    renderDrawer(true, onClose);
    const overlay = document.querySelector('[data-slot="drawer-overlay"]');
    expect(overlay).not.toBeNull();
    await user.click(overlay as Element);
    expect(onClose).toHaveBeenCalled();
  });
});
