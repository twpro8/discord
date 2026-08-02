// shared
import { api } from "@/shared/api/axios";

// entities
import type { Server } from "../../../entities/server/model/types";

/** Fetches all servers for the current user. */
export async function getMyServers(): Promise<Server[]> {
  const response = await api.get<Server[]>("/servers");
  return response.data;
}
