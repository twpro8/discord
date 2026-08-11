// react
import { useState } from "react";

// third party
import { isTauri } from "@tauri-apps/api/core";
import { Settings } from "lucide-react";

// shared
import { Modal } from "@/shared/ui/modal";

// relative
import { BackendUrlForm } from "./BackendUrlForm";

/**
 * Lets an unauthenticated user point the desktop app at a self-hosted
 * backend before signing in — the full Settings dialog's Server tab is
 * only reachable from the authenticated sidebar, which doesn't exist yet
 * at this point.
 */
export function ServerSettingsButton() {
  const [open, setOpen] = useState(false);

  if (!isTauri()) return null;

  return (
    <>
      <button
        type="button"
        aria-label="Server settings"
        onClick={() => setOpen(true)}
        className="fixed top-4 right-4 flex h-10 w-10 items-center justify-center rounded-2xl border border-border bg-background text-foreground transition hover:bg-muted"
      >
        <Settings className="h-5 w-5" />
      </button>
      <Modal
        open={open}
        onClose={() => setOpen(false)}
        className="max-w-md p-6"
      >
        <BackendUrlForm />
      </Modal>
    </>
  );
}
