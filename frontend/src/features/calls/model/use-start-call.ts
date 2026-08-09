// third party
import { toast } from "sonner";

// features
import { socketSend } from "@/features/realtime/model/socket-sender";

// relative
import { microphoneErrorMessage } from "./microphone-error";
import { useCallStore } from "./use-call-store";
import { getIceServers } from "./use-ice-servers";
import { attachLocalStream, createPeerConnection } from "./webrtc-session";

/** Starts an outgoing call: requests the mic, fetches ICE servers, then
 * sends the invite. Mirrors useSendTyping's shape — imperative socket
 * sends, no store subscription needed inside the hook itself. */
export function useStartCall() {
  return {
    startCall: async (
      chatId: string,
      calleeId: string,
      peerName: string,
    ): Promise<void> => {
      if (useCallStore.getState().phase !== "idle") return;

      // Requested immediately on click, before the invite is even sent:
      // avoids ringing the callee and then failing, and removes the
      // post-accept latency of a permission prompt + getUserMedia before
      // an offer can be created.
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (error) {
        toast.error(microphoneErrorMessage(error));
        return;
      }

      let iceServers: RTCIceServer[];
      try {
        iceServers = await getIceServers();
      } catch {
        stream.getTracks().forEach((track) => track.stop());
        toast.error("Couldn't start call — check your connection.");
        return;
      }

      const callId = crypto.randomUUID();
      createPeerConnection(iceServers);
      attachLocalStream(stream);
      useCallStore.getState().beginOutgoingCall({
        callId,
        chatId,
        peerId: calleeId,
        peerName,
        localStream: stream,
      });
      socketSend({
        type: "call.invite",
        call_id: callId,
        chat_id: chatId,
        callee_id: calleeId,
      });
    },
  };
}
