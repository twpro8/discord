// shared
import { api } from "@/shared/api/axios";

// entities
import type { Server } from "../../../entities/server/model/types";

/** Input for creating a new server. */
export interface CreateServerInput {
  name: string;
  description: string | null;
}

/** Creates a new server. */
export async function createServer(input: CreateServerInput): Promise<Server> {
  const response = await api.post<Server>("/servers", input);
  return response.data;
}
