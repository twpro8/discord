// react
import { useState } from "react";

// third party
import { toast } from "sonner";

// shared
import {
  clearBackendUrlOverride,
  readBackendUrlOverride,
  saveBackendUrlOverride,
} from "@/shared/config/backend";
import { API_BASE_URL } from "@/shared/config/env";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

/** Repoints the installed desktop app at a self-hosted backend, persisted locally. */
export function BackendUrlForm() {
  const [url, setUrl] = useState(() => readBackendUrlOverride() ?? "");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const result = saveBackendUrlOverride(url);
    if (!result.ok) {
      toast.error(result.error);
      return;
    }
    toast.success("Server updated — reloading…");
    window.location.reload();
  }

  function handleReset() {
    clearBackendUrlOverride();
    toast.success("Server reset to default — reloading…");
    window.location.reload();
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="grid gap-2">
        <Label htmlFor="settings-server-url">Server URL</Label>
        <Input
          id="settings-server-url"
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder={API_BASE_URL}
          autoComplete="off"
          required
        />
        <p className="text-xs text-muted-foreground">
          Point this app at your own self-hosted Lumiere backend. Saving reloads
          the app and signs you out of the previous server.
        </p>
      </div>

      <div className="flex gap-2">
        <Button type="submit">Save &amp; reload</Button>
        <Button type="button" variant="outline" onClick={handleReset}>
          Reset to default
        </Button>
      </div>
    </form>
  );
}
