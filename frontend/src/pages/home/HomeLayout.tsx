// react
import { useEffect, useState } from "react";

// third party
import { Outlet, useMatchRoute } from "@tanstack/react-router";

// shared
import { getUserChannel } from "@/shared/api/socket";
import { breakpoints } from "@/shared/helpers/breakpoints";
import { useMediaQuery } from "@/shared/helpers/use-media-query";
import { Drawer } from "@/shared/ui/drawer";
import { useShellDrawer } from "@/shared/ui/shell-drawer";

// features
import { useIncomingCall } from "@/features/calls/model/use-incoming-call";
import { useOutgoingCall } from "@/features/calls/model/use-outgoing-call";
import { useOutgoingCallEvents } from "@/features/calls/model/use-outgoing-call-events";
import { useVoiceRoom } from "@/features/calls/model/use-voice-room";
import { useWebRTC } from "@/features/calls/model/use-webRTC";
import { CallWindow } from "@/features/calls/ui/CallWindow";
import { ChannelSidebar } from "@/features/channels/ui/ChannelSidebar";
import { CreateChannelModal } from "@/features/channels/ui/CreateChannelModal";
import { FriendPanel } from "@/features/friends/ui/FriendPanel";
import { useCurrentUser } from "@/features/profile/model/use-current-user";
import { RealtimeProvider } from "@/features/realtime/RealtimeProvider";
import { CreateServerModal } from "@/features/servers/ui/CreateServerModal";
import { ServerMemberPanel } from "@/features/servers/ui/ServerMemberPanel";
import { ServerSidebar } from "@/features/servers/ui/ServerSidebar";

/** Authenticated shell with adaptive sidebars and the content outlet. */
export default function HomeLayout() {
  const [isCreateServerOpen, setIsCreateServerOpen] = useState(false);
  const [isCreateChannelOpen, setIsCreateChannelOpen] = useState(false);

  const { data: user } = useCurrentUser();
  const userId = user?.id;
  const { callerId, acceptedCallId, acceptCall, dismiss } =
    useIncomingCall(userId);
  useOutgoingCallEvents(userId);
  const outgoingPeerId = useOutgoingCall((state) => state.peerId);
  const outgoingAcceptedCallId = useOutgoingCall(
    (state) => state.acceptedCallId,
  );
  const clearOutgoing = useOutgoingCall((state) => state.clear);

  const voiceChannelId = useVoiceRoom((s) => s.channelId);
  const voiceRoomId = useVoiceRoom((s) => s.roomId);
  const leaveVoice = useVoiceRoom((s) => s.leave);

  const calleeWebRTC = useWebRTC({
    callId: acceptedCallId,
    role: "callee",
  });

  const callerWebRTC = useWebRTC({
    callId: outgoingAcceptedCallId,
    role: "caller",
  });

  const voiceWebRTC = useWebRTC({
    roomId: voiceRoomId,
    role: "caller",
  });

  function handleCancelOutgoing() {
    callerWebRTC.hangup();
    if (userId && outgoingPeerId) {
      getUserChannel(userId).push("cancel_call", {
        target_user_id: outgoingPeerId,
      });
    }
    clearOutgoing();
  }

  function handleHangupIncoming() {
    calleeWebRTC.hangup();
    dismiss();
  }

  function handleLeaveVoice() {
    voiceWebRTC.hangup();
    leaveVoice();
  }

  const isDesktop = useMediaQuery(breakpoints.desktop);
  const isMobile = useMediaQuery(breakpoints.mobile);
  const {
    isServersOpen,
    isChannelsOpen,
    isFriendsOpen,
    closeServers,
    closeChannels,
    closeFriends,
  } = useShellDrawer();

  const serversInDrawer = isMobile;
  const friendsInDrawer = !isDesktop;

  const matchRoute = useMatchRoute();
  const serverParams = matchRoute({ to: "/home/servers/$serverId" });
  const isServerRoute = serverParams !== false;
  const serverId = isServerRoute ? serverParams.serverId : undefined;
  const channelsInDrawer = isMobile;
  const rightLabel = isServerRoute ? "Members" : "Friends";

  useEffect(() => {
    if (!serversInDrawer) closeServers();
    if (!channelsInDrawer) closeChannels();
    if (!friendsInDrawer) closeFriends();
  }, [
    serversInDrawer,
    channelsInDrawer,
    friendsInDrawer,
    closeServers,
    closeChannels,
    closeFriends,
  ]);

  return (
    <RealtimeProvider>
      <div className="flex h-dvh w-full overflow-hidden bg-canvas">
        {serversInDrawer ? (
          <Drawer
            open={isServersOpen}
            onClose={closeServers}
            side="left"
            label="Servers"
          >
            <ServerSidebar
              onCreateServerClick={() => setIsCreateServerOpen(true)}
            />
          </Drawer>
        ) : (
          <ServerSidebar
            onCreateServerClick={() => setIsCreateServerOpen(true)}
          />
        )}

        {channelsInDrawer && isServerRoute && serverId ? (
          <Drawer
            open={isChannelsOpen}
            onClose={closeChannels}
            side="left"
            label="Channels"
          >
            <ChannelSidebar
              serverId={serverId}
              onCreateChannel={() => setIsCreateChannelOpen(true)}
            />
          </Drawer>
        ) : isServerRoute && serverId ? (
          <ChannelSidebar
            serverId={serverId}
            onCreateChannel={() => setIsCreateChannelOpen(true)}
          />
        ) : null}

        <main className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </main>

        {friendsInDrawer ? (
          <Drawer
            open={isFriendsOpen}
            onClose={closeFriends}
            side="right"
            label={rightLabel}
          >
            {isServerRoute && serverId ? (
              <ServerMemberPanel serverId={serverId} />
            ) : (
              <FriendPanel />
            )}
          </Drawer>
        ) : isServerRoute && serverId ? (
          <ServerMemberPanel serverId={serverId} />
        ) : (
          <FriendPanel />
        )}

        <CreateServerModal
          open={isCreateServerOpen}
          onClose={() => setIsCreateServerOpen(false)}
        />

        {serverId && (
          <CreateChannelModal
            serverId={serverId}
            open={isCreateChannelOpen}
            onClose={() => setIsCreateChannelOpen(false)}
          />
        )}

        <CallWindow
          mode="incoming"
          id={callerId}
          active={Boolean(acceptedCallId)}
          muted={calleeWebRTC.muted}
          cameraEnabled={calleeWebRTC.cameraEnabled}
          screenSharing={calleeWebRTC.screenSharing}
          onClose={acceptedCallId ? handleHangupIncoming : dismiss}
          onClick={acceptCall}
          onToggleMute={calleeWebRTC.toggleMute}
          onToggleCamera={calleeWebRTC.toggleCamera}
          onToggleScreenShare={
            calleeWebRTC.screenSharing
              ? calleeWebRTC.stopScreenShare
              : calleeWebRTC.startScreenShare
          }
          remoteStream={calleeWebRTC.remoteStream}
          remoteVideoStream={calleeWebRTC.remoteVideoStream}
          remoteScreenStream={calleeWebRTC.remoteScreenStream}
          remoteStreams={calleeWebRTC.remoteStreams}
          localCameraStream={calleeWebRTC.localVideoStream}
          localScreenStream={calleeWebRTC.screenStream}
        />
        <CallWindow
          mode="outgoing"
          id={outgoingPeerId}
          active={Boolean(outgoingAcceptedCallId)}
          muted={callerWebRTC.muted}
          cameraEnabled={callerWebRTC.cameraEnabled}
          screenSharing={callerWebRTC.screenSharing}
          onClose={handleCancelOutgoing}
          onToggleMute={callerWebRTC.toggleMute}
          onToggleCamera={callerWebRTC.toggleCamera}
          onToggleScreenShare={
            callerWebRTC.screenSharing
              ? callerWebRTC.stopScreenShare
              : callerWebRTC.startScreenShare
          }
          remoteStream={callerWebRTC.remoteStream}
          remoteVideoStream={callerWebRTC.remoteVideoStream}
          remoteScreenStream={callerWebRTC.remoteScreenStream}
          remoteStreams={callerWebRTC.remoteStreams}
          localCameraStream={callerWebRTC.localVideoStream}
          localScreenStream={callerWebRTC.screenStream}
        />
        {/* Unified voice channel room — same component, same WebRTC, persistent room:channel:* */}
        <CallWindow
          mode="outgoing"
          id={voiceChannelId}
          active={Boolean(voiceRoomId)}
          muted={voiceWebRTC.muted}
          cameraEnabled={voiceWebRTC.cameraEnabled}
          screenSharing={voiceWebRTC.screenSharing}
          onClose={handleLeaveVoice}
          onToggleMute={voiceWebRTC.toggleMute}
          onToggleCamera={voiceWebRTC.toggleCamera}
          onToggleScreenShare={
            voiceWebRTC.screenSharing
              ? voiceWebRTC.stopScreenShare
              : voiceWebRTC.startScreenShare
          }
          remoteStream={voiceWebRTC.remoteStream}
          remoteVideoStream={voiceWebRTC.remoteVideoStream}
          remoteScreenStream={voiceWebRTC.remoteScreenStream}
          remoteStreams={voiceWebRTC.remoteStreams}
          localCameraStream={voiceWebRTC.localVideoStream}
          localScreenStream={voiceWebRTC.screenStream}
        />
      </div>
    </RealtimeProvider>
  );
}
