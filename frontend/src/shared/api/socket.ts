// third party
import { Socket, type Channel } from "phoenix";

// relative
import { CALL_SERVER_URL } from "../config/env";

// Phoenix call server endpoint. The call server is a separate app from
// the Lumiere backend and has no shared config channel with it.

let socket: Socket | null = null;
let userChannel: Channel | null = null;
let joinedUserId: string | null = null;
let callChannel: Channel | null = null;
let joinedCallId: string | null = null;

/**
 * Returns the current user's `user:{id}` Phoenix channel, connecting the
 * socket and joining it exactly once. A different user id tears down the
 * previous connection first, so a logout/login-as-someone-else within
 * the same session doesn't stack connections. Call this both when the
 * user enters the app (HomeLayout) and from call UI; it's idempotent.
 */
export function getUserChannel(userId: string): Channel {
  if (socket && joinedUserId !== userId) {
    socket.disconnect();
    socket = null;
    joinedUserId = null;
  }

  if (!socket) {
    socket = new Socket(CALL_SERVER_URL);
    socket.connect();
  }

  let channel = userChannel;
  if (!channel) {
    channel = socket.channel(`user:${userId}`);
    channel.join();
    userChannel = channel;
  }

  joinedUserId = userId;
  return channel;
}

/** Subscribes the current user's `user:{id}` channel to incoming calls. */
export function subscribeToIncomingCalls(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel) return;
  userChannel.on("incoming_call", callback);
}

/** Subscribes the current user's `user:{id}` channel to `declined_call`
 * (their outgoing call was declined by the callee). The payload carries
 * the callee's id as `target_user_id`. */
export function subscribeToDeclinedCall(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel) return;
  userChannel.on("declined_call", callback);
}

/** Subscribes the current user's `user:{id}` channel to `call_cancelled`
 * (an incoming call was cancelled by the caller). The payload carries the
 * caller's id as `caller_id`. */
export function subscribeToCallCancelled(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel) return;
  userChannel.on("call_cancelled", callback);
}

/** Subscribes the current user's `user:{id}` channel to `call_accepted`
 * (the callee accepted the call). */
export function subscribeToCallAccepted(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel) return;
  userChannel.on("call_accepted", callback);
}

/** Joins the `room:{roomId}` channel for WebRTC signaling relay.
 * Unified room for 1:1, group and server voice — `call:{id}` is kept as alias.
 * Leaves any previously joined room channel first. */
export function getRoomChannel(roomId: string): Channel {
  if (callChannel && joinedCallId !== roomId) {
    callChannel.leave();
    callChannel = null;
    joinedCallId = null;
  }

  if (!callChannel) {
    if (!socket) {
      socket = new Socket(CALL_SERVER_URL);
      socket.connect();
    }
    // Phoenix server joins both "room:" and "call:" topics (alias for backwards compat).
    callChannel = socket.channel(`room:${roomId}`);
    callChannel.join();
    joinedCallId = roomId;
  }

  return callChannel;
}

/** Alias for backwards compat: `call:{callId}` == `room:{roomId}`. */
export function getCallChannel(callId: string): Channel {
  return getRoomChannel(callId);
}

/** Leaves the current room channel and resets state. */
export function leaveRoomChannel(): void {
  if (callChannel) {
    callChannel.leave();
    callChannel = null;
    joinedCallId = null;
  }
}

/** Alias for backwards compat. */
export function leaveCallChannel(): void {
  leaveRoomChannel();
}
