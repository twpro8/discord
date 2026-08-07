// relative

// shared
import { cn } from "@/shared/helpers/utils";

import { Dialog, DialogContent } from "./dialog";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
}

/** Simplified dialog wrapper with open/close control. */
export function Modal({ open, onClose, children, className }: ModalProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className={cn(className)}>{children}</DialogContent>
    </Dialog>
  );
}
