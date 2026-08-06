// shared
import { api } from "@/shared/api/axios";

// entities
import type { Channel } from "../../../entities/channel/model/types";

/** Fetches all channels for a server. */
export async function getServerChannels(serverId: string): Promise<Channel[]> {
  const response = await api.get<Channel[]>(`/servers/${serverId}/channels`);
  return response.data;
}
