// third party
import { Socket, type Channel } from "phoenix";

// Phoenix call server endpoint. The call server is a separate app from
// the Lumiere backend and has no shared config channel with it.
const CALL_SOCKET_URL = "ws://localhost:4000/socket";

let socket: Socket | null = null;
let userChannel: Channel | null = null;
let joinedUserId: string | null = null;
let incomingCallBound = false;
let declinedCallBound = false;
let callCancelledBound = false;

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
    incomingCallBound = false;
    declinedCallBound = false;
    callCancelledBound = false;
  }

  if (!socket) {
    socket = new Socket(CALL_SOCKET_URL);
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

/** Subscribes the current user's `user:{id}` channel to incoming calls,
 * exactly once per channel lifetime. Call after joining (HomeLayout). */
export function subscribeToIncomingCalls(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel || incomingCallBound) return;
  userChannel.on("incoming_call", callback);
  incomingCallBound = true;
}

/** Subscribes the current user's `user:{id}` channel to `declined_call`
 * (their outgoing call was declined by the callee), exactly once per
 * channel lifetime. The payload carries the callee's id as
 * `target_user_id`. */
export function subscribeToDeclinedCall(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel || declinedCallBound) return;
  userChannel.on("declined_call", callback);
  declinedCallBound = true;
}

/** Subscribes the current user's `user:{id}` channel to `call_cancelled`
 * (an incoming call was cancelled by the caller), exactly once per
 * channel lifetime. The payload carries the caller's id as `caller_id`. */
export function subscribeToCallCancelled(
  callback: (payload: unknown) => void,
): void {
  if (!userChannel || callCancelledBound) return;
  userChannel.on("call_cancelled", callback);
  callCancelledBound = true;
}
