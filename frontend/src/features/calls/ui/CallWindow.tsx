// third party
import { Mic, MicOff, MonitorUp, Video, VideoOff } from "lucide-react";

// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

import type { RemotePeerStreams } from "../model/use-peer-connections";
// relative
import { useUser } from "../model/use-user";

/** Call window — unified room for 1:1 / group / server voice.
 *  B-mode: camera and screen share as independent tracks (2 videos per peer).
 *  Screen is main stage, camera PiP. Falls back to avatar+audio when no video. */
export function CallWindow({
  mode,
  id,
  active,
  muted,
  cameraEnabled,
  screenSharing,
  onClose,
  onClick,
  onToggleMute,
  onToggleCamera,
  onToggleScreenShare,
  remoteStream,
  remoteVideoStream,
  remoteScreenStream,
  remoteStreams,
  localCameraStream,
  localScreenStream,
}: {
  mode: "incoming" | "outgoing";
  id: string | null;
  active?: boolean;
  muted?: boolean;
  cameraEnabled?: boolean;
  screenSharing?: boolean;
  onClose: () => void;
  onClick?: () => void;
  onToggleMute?: () => void;
  onToggleCamera?: () => void;
  onToggleScreenShare?: () => void;
  remoteStream?: MediaStream | null;
  remoteVideoStream?: MediaStream | null;
  remoteScreenStream?: MediaStream | null;
  remoteStreams?: Map<string, RemotePeerStreams> | null;
  localCameraStream?: MediaStream | null;
  localScreenStream?: MediaStream | null;
}) {
  const { data: user, isLoading } = useUser(id);
  const name = user?.name ?? user?.username;

  const hasLocalVideo = Boolean(localCameraStream || localScreenStream);
  const hasRemoteVideo = Boolean(
    remoteVideoStream ||
    remoteScreenStream ||
    (remoteStreams &&
      Array.from(remoteStreams.values()).some(
        (p) => p.videoStream || p.screenStream,
      )),
  );
  const hasAnyVideo = hasLocalVideo || hasRemoteVideo;

  const remotePeers: Array<{ key: string; streams: RemotePeerStreams }> = [];
  if (remoteStreams && remoteStreams.size > 0) {
    remoteStreams.forEach((streams, key) => remotePeers.push({ key, streams }));
  } else if (remoteVideoStream || remoteScreenStream || remoteStream) {
    remotePeers.push({
      key: "remote",
      streams: {
        audioStream: remoteStream ?? null,
        videoStream: remoteVideoStream ?? null,
        screenStream: remoteScreenStream ?? null,
      },
    });
  }

  const hasScreen = Boolean(
    localScreenStream || remotePeers.some((p) => p.streams.screenStream),
  );

  return (
    <Modal
      open={Boolean(id)}
      onClose={onClose}
      className={
        hasAnyVideo && active
          ? "max-w-[min(95vw,1280px)] w-[95vw] max-h-[85dvh] overflow-y-auto"
          : undefined
      }
    >
      <div className="flex flex-col items-center gap-4 py-2 text-center sm:py-4">
        {!hasAnyVideo || !active ? (
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
                    : screenSharing
                      ? "Screen sharing"
                      : cameraEnabled
                        ? "Video on"
                        : "Voice call in progress"
                  : mode === "incoming"
                    ? "Voice call incoming"
                    : "Ringing their device"}
              </p>
            </div>
          </div>
        ) : (
          <h2 className="text-sm font-medium text-muted-foreground">
            {name ? `In call with ${name}` : "In call"}
            {screenSharing ? " · sharing screen" : ""}
            {cameraEnabled ? " · camera on" : ""}
          </h2>
        )}

        {active && hasAnyVideo && (
          <div className="flex w-full flex-col gap-4">
            {/* Local preview when no remote yet — larger, not tiny */}
            {hasLocalVideo && remotePeers.length === 0 && (
              <div className="flex w-full flex-col gap-3">
                {localScreenStream && (
                  <div className="relative aspect-video w-full overflow-hidden rounded-xl bg-surface-raised ring-1 ring-border">
                    <video
                      ref={(el) => {
                        if (el) el.srcObject = localScreenStream;
                      }}
                      autoPlay
                      playsInline
                      muted
                      className="h-full w-full object-contain"
                    />
                    {localCameraStream && (
                      <video
                        ref={(el) => {
                          if (el) el.srcObject = localCameraStream;
                        }}
                        autoPlay
                        playsInline
                        muted
                        className="absolute right-3 bottom-3 h-24 w-36 rounded-lg bg-surface-raised object-cover shadow-raised ring-1 ring-white/10 sm:h-28 sm:w-44"
                        style={{ transform: "scaleX(-1)" }}
                      />
                    )}
                    <span className="absolute top-3 left-3 rounded-md bg-overlay px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
                      Your screen
                    </span>
                  </div>
                )}
                {!localScreenStream && localCameraStream && (
                  <div className="relative aspect-video w-full overflow-hidden rounded-xl bg-surface-raised ring-1 ring-border">
                    <video
                      ref={(el) => {
                        if (el) el.srcObject = localCameraStream;
                      }}
                      autoPlay
                      playsInline
                      muted
                      className="h-full w-full object-cover"
                      style={{ transform: "scaleX(-1)" }}
                    />
                    <span className="absolute right-3 bottom-3 rounded-md bg-overlay px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
                      You
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Remote — 1:1: screen main stage + camera PiP; camera-only: side-by-side equal; group: grid */}
            {remotePeers.length > 0 && (
              <div
                className={
                  remotePeers.length === 1 && hasScreen
                    ? "flex flex-col gap-3"
                    : remotePeers.length === 1
                      ? "flex flex-col gap-3"
                      : "grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 auto-rows-fr"
                }
              >
                {remotePeers.map(({ key, streams }) => {
                  const hasRemoteScreen = Boolean(streams.screenStream);
                  const hasRemoteCamera = Boolean(streams.videoStream);

                  // Screen sharing — main stage
                  if (hasRemoteScreen) {
                    return (
                      <div
                        key={key}
                        className="relative aspect-video w-full overflow-hidden rounded-xl bg-surface-raised ring-1 ring-border"
                      >
                        <video
                          ref={(el) => {
                            if (el) el.srcObject = streams.screenStream;
                          }}
                          autoPlay
                          playsInline
                          className="h-full w-full object-contain"
                        />
                        {/* Remote camera PiP on top of their screen */}
                        {hasRemoteCamera && (
                          <video
                            ref={(el) => {
                              if (el) el.srcObject = streams.videoStream;
                            }}
                            autoPlay
                            playsInline
                            className="absolute right-3 bottom-3 h-24 w-36 rounded-lg bg-surface-raised object-cover shadow-raised ring-1 ring-white/10 sm:h-28 sm:w-44"
                          />
                        )}
                        {/* Local camera PiP when both share — show your face too */}
                        {localCameraStream && !hasRemoteCamera && (
                          <video
                            ref={(el) => {
                              if (el) el.srcObject = localCameraStream;
                            }}
                            autoPlay
                            playsInline
                            muted
                            className="absolute left-3 bottom-3 hidden h-24 w-36 rounded-lg bg-surface-raised object-cover shadow-raised ring-1 ring-white/10 sm:block sm:h-28 sm:w-44"
                            style={{ transform: "scaleX(-1)" }}
                          />
                        )}
                        <span className="absolute top-3 left-3 rounded-md bg-overlay px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
                          {name ?? "Remote"}&apos;s screen
                        </span>
                      </div>
                    );
                  }

                  if (hasRemoteCamera) {
                    return (
                      <div
                        key={key}
                        className="relative aspect-video w-full overflow-hidden rounded-xl bg-surface-raised ring-1 ring-border"
                      >
                        <video
                          ref={(el) => {
                            if (el) el.srcObject = streams.videoStream;
                          }}
                          autoPlay
                          playsInline
                          className="h-full w-full object-cover"
                        />
                        {/* Local camera PiP when viewing remote camera */}
                        {localCameraStream && remotePeers.length === 1 && (
                          <video
                            ref={(el) => {
                              if (el) el.srcObject = localCameraStream;
                            }}
                            autoPlay
                            playsInline
                            muted
                            className="absolute right-3 bottom-3 h-24 w-36 rounded-lg bg-surface-raised object-cover shadow-raised ring-1 ring-white/10 sm:h-28 sm:w-44"
                            style={{ transform: "scaleX(-1)" }}
                          />
                        )}
                        {/* If also sharing locally, show local screen as second large stage below — handled by localScreen block above */}
                      </div>
                    );
                  }

                  // Audio only fallback
                  return (
                    <div
                      key={key}
                      className="flex aspect-video w-full items-center justify-center rounded-xl bg-surface-raised ring-1 ring-border"
                    >
                      <Avatar
                        name={name ?? "?"}
                        src={user?.avatar_url}
                        className="h-16 w-16 text-xl"
                      />
                    </div>
                  );
                })}
              </div>
            )}

            {/* Local screen PiP when remote has screen and local also shares — show local screen as second stage */}
            {hasLocalVideo &&
              localScreenStream &&
              remotePeers.some((p) => p.streams.screenStream) && (
                <div className="relative aspect-video w-full overflow-hidden rounded-xl bg-surface-raised ring-1 ring-border">
                  <video
                    ref={(el) => {
                      if (el) el.srcObject = localScreenStream;
                    }}
                    autoPlay
                    playsInline
                    muted
                    className="h-full w-full object-contain"
                  />
                  <span className="absolute top-3 left-3 rounded-md bg-overlay px-2 py-1 text-xs font-medium text-white backdrop-blur-sm">
                    Your screen
                  </span>
                  {localCameraStream && (
                    <video
                      ref={(el) => {
                        if (el) el.srcObject = localCameraStream;
                      }}
                      autoPlay
                      playsInline
                      muted
                      className="absolute right-3 bottom-3 h-24 w-36 rounded-lg bg-surface-raised object-cover shadow-raised ring-1 ring-white/10 sm:h-28 sm:w-44"
                      style={{ transform: "scaleX(-1)" }}
                    />
                  )}
                </div>
              )}
          </div>
        )}

        {!hasAnyVideo && remoteStream && (
          <audio
            ref={(el) => {
              if (el) el.srcObject = remoteStream;
            }}
            autoPlay
            playsInline
          />
        )}
        {hasAnyVideo &&
          remotePeers.map(({ key, streams }) =>
            streams.audioStream ? (
              <audio
                key={`audio-${key}`}
                ref={(el) => {
                  if (el) el.srcObject = streams.audioStream;
                }}
                autoPlay
                playsInline
                hidden
              />
            ) : null,
          )}

        <div className="sticky bottom-0 -mx-4 flex flex-wrap justify-center gap-3 bg-canvas/80 px-4 pt-2 backdrop-blur-sm sm:mx-0 sm:px-0">
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
                variant={cameraEnabled ? "default" : "outline"}
                onClick={onToggleCamera}
                aria-label={
                  cameraEnabled ? "Turn off camera" : "Turn on camera"
                }
                title={cameraEnabled ? "Turn off camera" : "Turn on camera"}
              >
                {cameraEnabled ? (
                  <Video className="mr-2 h-4 w-4" />
                ) : (
                  <VideoOff className="mr-2 h-4 w-4" />
                )}
                {cameraEnabled ? "Camera off" : "Camera"}
              </Button>
              <Button
                type="button"
                size="lg"
                variant={screenSharing ? "default" : "outline"}
                onClick={onToggleScreenShare}
                aria-label={screenSharing ? "Stop sharing" : "Share screen"}
                title={screenSharing ? "Stop sharing" : "Share screen"}
              >
                <MonitorUp className="mr-2 h-4 w-4" />
                {screenSharing ? "Stop share" : "Share"}
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
