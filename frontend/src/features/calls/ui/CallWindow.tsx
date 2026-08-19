// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

// relative
import { useUser } from "../model/use-user";

/** Call window showing the counterparty (avatar + name) with Accept and
 * Decline buttons. Incoming shows who's calling; outgoing shows who's
 * being called. Accept is a placeholder for now; Decline closes the
 * window via `onClose` — the wiring passed in (e.g. HomeLayout) may also
 * notify the call server that the call was declined/cancelled. */
export function CallWindow({
  mode,
  id,
  onClose,
}: {
  mode: "incoming" | "outgoing";
  id: string | null;
  onClose: () => void;
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
              {isLoading
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
              {mode === "incoming"
                ? "Voice call incoming"
                : "Ringing their device"}
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button type="button" size="lg">
            Accept
          </Button>
          <Button type="button" size="lg" variant="outline" onClick={onClose}>
            Decline
          </Button>
        </div>
      </div>
    </Modal>
  );
}
