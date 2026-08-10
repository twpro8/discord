type SendFn = (data: unknown) => void;

let sendFn: SendFn = () => {};

/**
 * Set by RealtimeProvider on connect/disconnect. Not reactive — callers
 * invoke this imperatively from event handlers, never during render, so a
 * plain module ref (not a Zustand store — see shell-drawer.ts for what
 * that's for) is the right amount of machinery.
 */
export function setSocketSend(fn: SendFn): void {
  sendFn = fn;
}

/** Sends a frame over the realtime socket, or no-ops if disconnected. */
export function socketSend(data: unknown): void {
  sendFn(data);
}
