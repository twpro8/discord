/** Channel kind, aligned with the backend ChannelType enum. */
export type ChannelType = "text" | "voice";

/** Channel domain model, aligned with the backend ChannelResponse schema. */
export interface Channel {
  id: string;
  name: string;
  server_id: string;
  type: ChannelType;
  topic: string | null;
  position: number;
  last_sequence: number;
  is_private: boolean;
  created_at: string;
  updated_at: string;
}
