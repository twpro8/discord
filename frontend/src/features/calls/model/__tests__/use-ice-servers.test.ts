import { vi } from "vitest";

import { getTurnCredentials } from "../../api/get-turn-credentials";
import { getIceServers } from "../use-ice-servers";

vi.mock("../../api/get-turn-credentials", () => ({
  getTurnCredentials: vi.fn(),
}));

const getTurnCredentialsMock = vi.mocked(getTurnCredentials);

describe("getIceServers", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns the ice_servers list from the backend response", async () => {
    const iceServers = [{ urls: "stun:stun.example.com:19302" }];
    getTurnCredentialsMock.mockResolvedValue({ ice_servers: iceServers });

    await expect(getIceServers()).resolves.toEqual(iceServers);
  });

  it("propagates a fetch failure rather than falling back to a hardcoded list", async () => {
    getTurnCredentialsMock.mockRejectedValue(new Error("network error"));

    await expect(getIceServers()).rejects.toThrow("network error");
  });
});
