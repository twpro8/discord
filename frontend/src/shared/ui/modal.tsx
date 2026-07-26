// relative
import { Dialog, DialogContent } from "./dialog";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

/** Simplified dialog wrapper with open/close control. */
export function Modal({ open, onClose, children }: ModalProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent>{children}</DialogContent>
    </Dialog>
  );
}
