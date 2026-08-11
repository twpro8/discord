import { isTauri } from "@tauri-apps/api/core";
import { fetch as tauriFetch } from "@tauri-apps/plugin-http";

vi.mock("@tauri-apps/api/core", () => ({ isTauri: vi.fn() }));
vi.mock("@tauri-apps/plugin-http", () => ({ fetch: vi.fn() }));

describe("api axios instance Tauri adapter", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("keeps the default adapter in the web build", async () => {
    vi.mocked(isTauri).mockReturnValue(false);

    const { api } = await import("../axios");

    expect(api.defaults.adapter).toEqual(["xhr", "http", "fetch"]);
    expect(api.defaults.env?.fetch).toBeUndefined();
  });

  it("routes through the Tauri HTTP client's fetch adapter in the desktop app", async () => {
    vi.mocked(isTauri).mockReturnValue(true);

    const { api } = await import("../axios");

    expect(api.defaults.adapter).toBe("fetch");
    expect(api.defaults.env?.fetch).toBe(tauriFetch);
  });
});
