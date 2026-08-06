// shared
import { api } from "@/shared/api/axios";

// entities
import type {
  Channel,
  ChannelType,
} from "../../../entities/channel/model/types";

/** Input for creating a new channel. */
export interface CreateChannelInput {
  name: string;
  type: ChannelType;
  topic?: string | null;
}

/** Creates a new channel in a server. */
export async function createChannel(
  serverId: string,
  input: CreateChannelInput,
): Promise<Channel> {
  const response = await api.post<Channel>(
    `/servers/${serverId}/channels`,
    input,
  );
  return response.data;
}
