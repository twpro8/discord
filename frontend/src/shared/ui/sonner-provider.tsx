// third party
import { Toaster } from "sonner";

/** Toast notification provider mounted at the app root. */
export function SonnerProvider() {
  return (
    <Toaster
      position="top-right"
      richColors
      closeButton
      expand
      toastOptions={{
        classNames: {
          toast: "border-border bg-background text-foreground",
          success: "border-emerald-500/20 text-emerald-600",
          error: "border-destructive/20 text-destructive",
        },
      }}
    />
  );
}
