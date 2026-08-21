/** Minimal ambient types for the `phoenix` npm package, which ships no
 * declarations of its own. Only the surface the app uses is described:
 * connecting a Socket, joining a Channel, and pushing/receiving frames. */
declare module "phoenix" {
  export type Status = "ok" | "error" | "timeout";

  export class Push {
    receive(status: Status, callback: (response: unknown) => void): this;
  }

  export class Channel {
    join(): Push;
    push(event: string, payload: Record<string, unknown>): Push;
    on(event: string, callback: (payload: any) => void): number;
    off(event: string, ref?: number): void;
    leave(): Push;
  }

  export class Socket {
    constructor(endpoint: string, opts?: Record<string, unknown>);
    connect(): void;
    disconnect(): void;
    channel(topic: string, params?: Record<string, unknown>): Channel;
  }
}
