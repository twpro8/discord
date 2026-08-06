// react
import { useEffect, useState } from "react";

// third party
import { Hash, Volume2 } from "lucide-react";

// shared
import { cn } from "@/shared/helpers/utils";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Modal } from "@/shared/ui/modal";

// entities
import type { ChannelType } from "@/entities/channel/model/types";

// relative
import { useCreateChannel } from "../model/use-create-channel";

const CHANNEL_TYPES: {
  value: ChannelType;
  label: string;
  description: string;
  icon: typeof Hash;
}[] = [
  {
    value: "text",
    label: "Text",
    description: "Send and read messages",
    icon: Hash,
  },
  {
    value: "voice",
    label: "Voice",
    description: "Talk together in a voice channel",
    icon: Volume2,
  },
];

/** Modal form for creating a new channel in a server. */
export function CreateChannelModal({
  serverId,
  open,
  onClose,
}: {
  serverId: string;
  open: boolean;
  onClose: () => void;
}) {
  const [type, setType] = useState<ChannelType>("text");
  const [name, setName] = useState("");
  const [topic, setTopic] = useState("");
  const createChannel = useCreateChannel(serverId);

  useEffect(() => {
    if (open) {
      setType("text");
      setName("");
      setTopic("");
    }
  }, [open]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!name.trim()) return;
    createChannel.mutate(
      {
        name: name.trim(),
        type,
        topic: topic.trim() || null,
      },
      { onSuccess: onClose },
    );
  };

  return (
    <Modal open={open} onClose={onClose}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            Create a channel
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Add a channel to this server.
          </p>
        </div>
      </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium text-foreground">
            Channel type
          </label>
          <div className="grid gap-2 sm:grid-cols-2">
            {CHANNEL_TYPES.map((option) => {
              const Icon = option.icon;
              const isActive = type === option.value;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setType(option.value)}
                  aria-pressed={isActive}
                  className={cn(
                    "flex items-start gap-3 rounded-lg border p-3 text-left transition-colors",
                    isActive
                      ? "border-ring bg-accent-subtle"
                      : "border-border bg-surface-raised hover:bg-surface-hover",
                  )}
                >
                  <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                  <span>
                    <span className="block text-sm font-medium text-foreground">
                      {option.label}
                    </span>
                    <span className="block text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <label
            className="mb-1 block text-sm font-medium text-foreground"
            htmlFor="channel-name"
          >
            Channel name
          </label>
          <Input
            id="channel-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="new-channel"
            autoFocus
          />
        </div>

        <div>
          <label
            className="mb-1 block text-sm font-medium text-foreground"
            htmlFor="channel-topic"
          >
            Topic
          </label>
          <Input
            id="channel-topic"
            value={topic}
            onChange={(event) => setTopic(event.target.value)}
            placeholder="What is this channel about?"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={createChannel.isPending || !name.trim()}
          >
            {createChannel.isPending ? "Creating..." : "Create channel"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
