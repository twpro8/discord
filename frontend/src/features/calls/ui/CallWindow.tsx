// third party
import { Mic, MicOff } from "lucide-react";

// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

// relative
import { useUser } from "../model/use-user";

/** Call window showing the counterparty (avatar + name) with Accept,
 * Decline/Cancel, or Hang up buttons. `active` transitions the window
 * into an in-call state: text changes, a mute toggle and Hang up button
 * appear, and the remote audio stream plays. */
export function CallWindow({
  mode,
  id,
  active,
  muted,
  onClose,
  onClick,
  onToggleMute,
  remoteStream,
}: {
  mode: "incoming" | "outgoing";
  id: string | null;
  active?: boolean;
  muted?: boolean;
  onClose: () => void;
  onClick?: () => void;
  onToggleMute?: () => void;
  remoteStream?: MediaStream | null;
}) {
  const { data: user, isLoading } = useUser(id);
  const name = user?.name ?? user?.username;

  return (
    <Modal open={Boolean(id)} onClose={onClose}>
      <div className="flex flex-col items-center gap-4 py-4 text-center">
        <div className="flex flex-col items-center gap-3">
          <Avatar
            name={name ?? "?"}
            src={user?.avatar_url}
            className="h-16 w-16 text-xl"
          />
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              {active
                ? name
                  ? `In call with ${name}`
                  : "In call"
                : isLoading
                  ? mode === "incoming"
                    ? "Incoming call..."
                    : "Calling..."
                  : name
                    ? mode === "incoming"
                      ? `${name} is calling`
                      : `Calling ${name}...`
                    : mode === "incoming"
                      ? "Incoming call"
                      : "Calling..."}
            </h2>
            <p className="text-sm text-muted-foreground">
              {active
                ? muted
                  ? "Microphone muted"
                  : "Voice call in progress"
                : mode === "incoming"
                  ? "Voice call incoming"
                  : "Ringing their device"}
            </p>
          </div>
        </div>

        {remoteStream && (
          <audio
            ref={(el) => {
              if (el) el.srcObject = remoteStream;
            }}
            autoPlay
            playsInline
          />
        )}

        <div className="flex gap-3">
          {active ? (
            <>
              <Button
                type="button"
                size="lg"
                variant={muted ? "default" : "outline"}
                onClick={onToggleMute}
              >
                {muted ? (
                  <MicOff className="mr-2 h-4 w-4" />
                ) : (
                  <Mic className="mr-2 h-4 w-4" />
                )}
                {muted ? "Unmute" : "Mute"}
              </Button>
              <Button
                type="button"
                size="lg"
                variant="destructive"
                onClick={onClose}
              >
                Hang up
              </Button>
            </>
          ) : (
            <>
              {mode === "incoming" && (
                <Button type="button" size="lg" onClick={onClick}>
                  Accept
                </Button>
              )}
              <Button
                type="button"
                size="lg"
                variant="outline"
                onClick={onClose}
              >
                {mode === "incoming" ? "Decline" : "Cancel"}
              </Button>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
}
