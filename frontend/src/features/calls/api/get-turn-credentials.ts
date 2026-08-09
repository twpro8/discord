// shared
import { api } from "@/shared/api/axios";

// relative
import type { IceServersResponse } from "../model/types";

/** Fetches short-lived ICE server credentials (STUN always, TURN if the
 * backend has it configured) for a call about to start. Not cached —
 * TURN credentials are time-limited, so this is called fresh at each
 * genuine call-start moment (outgoing call, incoming call accept). */
export async function getTurnCredentials(): Promise<IceServersResponse> {
  const response = await api.get<IceServersResponse>("/calls/turn-credentials");
  return response.data;
}
