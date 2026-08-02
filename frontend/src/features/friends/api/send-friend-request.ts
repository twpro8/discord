// shared
import { api } from "@/shared/api/axios";

/** Input for sending a friend request by username. */
export interface SendFriendRequestInput {
  username: string;
}

/** Sends a friend request to a user by username. */
export async function sendFriendRequest(
  input: SendFriendRequestInput,
): Promise<void> {
  await api.post("/friends/requests", input);
}
