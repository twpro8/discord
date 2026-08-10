// shared
import { api } from "@/shared/api/axios";

// relative
import type { ServerMemberWithUser } from "../model/types";

/** Fetches the member roster for a server. */
export async function getServerMembers(
  serverId: string,
): Promise<ServerMemberWithUser[]> {
  const response = await api.get<ServerMemberWithUser[]>(
    `/servers/${serverId}/members`,
  );
  return response.data;
}
