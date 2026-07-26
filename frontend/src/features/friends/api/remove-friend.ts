// shared
import { api } from "@/shared/api/axios";

/** Removes a friend from the user's friend list. */
export async function removeFriend(relationshipId: string): Promise<void> {
  await api.delete(`/friends/${relationshipId}`);
}
