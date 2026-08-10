// third party
import { toast } from "sonner";

// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

// features
import { useChatDetails } from "@/features/chats/model/use-chat-details";
import { socketSend } from "@/features/realtime/model/socket-sender";

// relative
import { ensureMicrophonePermission } from "../model/ensure-microphone-permission";
import { microphoneErrorMessage } from "../model/microphone-error";
import { useCallStore } from "../model/use-call-store";
import { getIceServers } from "../model/use-ice-servers";
import {
  attachLocalStream,
  createPeerConnection,
} from "../model/webrtc-session";

/** Incoming-call ringing UI, mounted once globally (see HomeLayout) —
 * shows whenever the call store's phase is "incoming_ringing". Mic
 * permission is requested only here, on the Accept click, not when the
 * invite first arrives. */
export function IncomingCallModal() {
  const phase = useCallStore((state) => state.phase);
  const callId = useCallStore((state) => state.callId);
  const chatId = useCallStore((state) => state.chatId);
  const storedPeerName = useCallStore((state) => state.peerName);
  const { data: chatDetails } = useChatDetails(chatId);
  const displayName = chatDetails?.peer_name ?? storedPeerName ?? "Someone";

  if (phase !== "incoming_ringing" || !callId) return null;

  const handleReject = () => {
    socketSend({ type: "call.reject", call_id: callId });
    useCallStore.getState().reset();
  };

  const handleAccept = async () => {
    try {
      await ensureMicrophonePermission();
    } catch (error) {
      // A real rejection, not a silent hang — the caller shouldn't wait
      // out the full ring timeout for this.
      toast.error(microphoneErrorMessage(error));
      socketSend({ type: "call.reject", call_id: callId });
      useCallStore.getState().reset();
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      // A real rejection, not a silent hang — the caller shouldn't wait
      // out the full ring timeout for this.
      toast.error(microphoneErrorMessage(error));
      socketSend({ type: "call.reject", call_id: callId });
      useCallStore.getState().reset();
      return;
    }

    let iceServers: RTCIceServer[];
    try {
      iceServers = await getIceServers();
    } catch {
      stream.getTracks().forEach((track) => track.stop());
      toast.error("Couldn't answer call — check your connection.");
      socketSend({ type: "call.reject", call_id: callId });
      useCallStore.getState().reset();
      return;
    }

    createPeerConnection(iceServers);
    attachLocalStream(stream);
    useCallStore.getState().transitionToConnecting(stream);
    socketSend({ type: "call.accept", call_id: callId });
  };

  return (
    <Modal open onClose={handleReject}>
      <div className="flex flex-col items-center gap-4 p-6">
        <Avatar name={displayName} className="h-16 w-16 text-2xl" />
        <div className="text-center">
          <p className="text-lg font-semibold text-foreground">{displayName}</p>
          <p className="text-sm text-muted-foreground">Incoming voice call…</p>
        </div>
        <div className="flex gap-3">
          <Button variant="destructive" onClick={handleReject}>
            Decline
          </Button>
          <Button variant="default" onClick={() => void handleAccept()}>
            Accept
          </Button>
        </div>
      </div>
    </Modal>
  );
}
