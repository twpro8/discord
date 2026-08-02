// react
import { useState } from "react";

// third party
import { toast } from "sonner";

// shared
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Modal } from "@/shared/ui/modal";

// relative
import { createServer } from "../api/create-server";
import { useServers } from "../model/use-servers";

/** Modal form for creating a new server. */
export function CreateServerModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { invalidate } = useServers();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!name.trim()) {
      toast.error("Server name is required");
      return;
    }

    setIsSubmitting(true);

    try {
      await createServer({
        name: name.trim(),
        description: description.trim() || null,
      });
      toast.success("Server created successfully");
      setName("");
      setDescription("");
      await invalidate();
      onClose();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to create server";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            Create a server
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Build your own space for friends and channels.
          </p>
        </div>
      </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label
            className="mb-1 block text-sm font-medium text-foreground"
            htmlFor="server-name"
          >
            Server name
          </label>
          <Input
            id="server-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="My server"
          />
        </div>

        <div>
          <label
            className="mb-1 block text-sm font-medium text-foreground"
            htmlFor="server-description"
          >
            Description
          </label>
          <textarea
            id="server-description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="min-h-24 w-full rounded-lg border border-input bg-surface-raised px-3 py-2 text-sm outline-none transition-colors placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            placeholder="What is this server about?"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create server"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
