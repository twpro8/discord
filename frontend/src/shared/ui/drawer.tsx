// react
import * as React from "react";

// third party
import { Dialog as DialogPrimitive } from "radix-ui";

// shared
import { cn } from "@/shared/helpers/utils";

type DrawerProps = {
  /** Whether the drawer is open. */
  open: boolean;
  /** Callback fired when the drawer requests to close. */
  onClose: () => void;
  /** Side the panel slides in from. */
  side?: "left" | "right";
  /** Accessible name describing the drawer's content. */
  label: string;
  className?: string;
  children: React.ReactNode;
};

/** Full-height overlay panel that slides in from a side of the viewport. */
export function Drawer({
  open,
  onClose,
  side = "right",
  label,
  className,
  children,
}: DrawerProps) {
  return (
    <DialogPrimitive.Root
      open={open}
      onOpenChange={(next) => {
        if (!next) onClose();
      }}
    >
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay
          data-slot="drawer-overlay"
          className="fixed inset-0 z-40 bg-overlay duration-150 data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0"
        />
        <DialogPrimitive.Content
          data-slot="drawer-content"
          data-side={side}
          aria-label={label}
          aria-describedby={undefined}
          className={cn(
            "fixed top-0 z-40 flex h-dvh flex-col bg-surface shadow-raised duration-150 outline-none data-open:animate-in data-closed:animate-out",
            side === "left"
              ? "left-0 border-r border-border data-open:slide-in-from-left data-closed:slide-out-to-left"
              : "right-0 border-l border-border data-open:slide-in-from-right data-closed:slide-out-to-right",
            className,
          )}
        >
          {children}
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}
