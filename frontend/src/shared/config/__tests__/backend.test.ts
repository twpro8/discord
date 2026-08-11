import {
  clearBackendUrlOverride,
  getApiBaseUrl,
  getWsEventsUrl,
  parseBackendUrl,
  readBackendUrlOverride,
  saveBackendUrlOverride,
} from "../backend";

function createStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => [...values.keys()][index] ?? null,
    removeItem: (key) => values.delete(key),
    setItem: (key, value) => values.set(key, value),
  };
}

describe("backend URL override", () => {
  beforeEach(() => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: createStorage(),
    });
    window.localStorage.clear();
  });

  describe("parseBackendUrl", () => {
    it("rejects an empty string", () => {
      expect(parseBackendUrl("")).toEqual({
        ok: false,
        error: "Server URL is required.",
      });
    });

    it("rejects a whitespace-only string", () => {
      expect(parseBackendUrl("   ")).toEqual({
        ok: false,
        error: "Server URL is required.",
      });
    });

    it("rejects a non-URL string", () => {
      expect(parseBackendUrl("not a url")).toEqual({
        ok: false,
        error: "Enter a valid URL, e.g. https://your-server.example.com.",
      });
    });

    it("rejects a non-http(s) protocol", () => {
      expect(parseBackendUrl("ws://example.com")).toEqual({
        ok: false,
        error: "Server URL must use http or https.",
      });
    });

    it("rejects a URL with a non-root path", () => {
      expect(parseBackendUrl("https://example.com/some/path")).toEqual({
        ok: false,
        error:
          "Server URL must be a plain address with no path, query, or fragment.",
      });
    });

    it("rejects a URL with a query string", () => {
      expect(parseBackendUrl("https://example.com?x=1")).toEqual({
        ok: false,
        error:
          "Server URL must be a plain address with no path, query, or fragment.",
      });
    });

    it("accepts a plain http origin with a port", () => {
      expect(parseBackendUrl("http://192.168.1.10:8000")).toEqual({
        ok: true,
        value: "http://192.168.1.10:8000",
      });
    });

    it("accepts a plain https origin", () => {
      expect(parseBackendUrl("https://chat.example.com")).toEqual({
        ok: true,
        value: "https://chat.example.com",
      });
    });

    it("normalizes a trailing slash to the same origin as no trailing slash", () => {
      const withSlash = parseBackendUrl("https://chat.example.com/");
      const withoutSlash = parseBackendUrl("https://chat.example.com");
      const doubleSlash = parseBackendUrl("https://chat.example.com//");

      expect(withSlash).toEqual({
        ok: true,
        value: "https://chat.example.com",
      });
      expect(withoutSlash).toEqual(withSlash);
      expect(doubleSlash).toEqual(withSlash);
    });

    it("trims surrounding whitespace before validating", () => {
      expect(parseBackendUrl("  https://chat.example.com  ")).toEqual({
        ok: true,
        value: "https://chat.example.com",
      });
    });
  });

  describe("persistence round-trip", () => {
    it("returns null when nothing is stored", () => {
      expect(readBackendUrlOverride()).toBeNull();
    });

    it("saves and reads back a validated override", () => {
      expect(saveBackendUrlOverride("https://chat.example.com/")).toEqual({
        ok: true,
        value: "https://chat.example.com",
      });
      expect(readBackendUrlOverride()).toBe("https://chat.example.com");
    });

    it("does not persist an invalid override", () => {
      expect(saveBackendUrlOverride("not a url").ok).toBe(false);
      expect(readBackendUrlOverride()).toBeNull();
    });

    it("clears a stored override", () => {
      saveBackendUrlOverride("https://chat.example.com");
      clearBackendUrlOverride();
      expect(readBackendUrlOverride()).toBeNull();
    });
  });

  describe("getApiBaseUrl / getWsEventsUrl", () => {
    it("falls back to the build-time default when no override is stored", () => {
      expect(getApiBaseUrl()).toBe("http://localhost:8000");
      expect(getWsEventsUrl()).toBe("ws://localhost:8000/api/v1/ws");
    });

    it("uses the stored override once one is saved", () => {
      saveBackendUrlOverride("http://192.168.1.10:9000");

      expect(getApiBaseUrl()).toBe("http://192.168.1.10:9000");
      expect(getWsEventsUrl()).toBe("ws://192.168.1.10:9000/api/v1/ws");
    });

    it("derives wss:// from an https:// override", () => {
      saveBackendUrlOverride("https://chat.example.com");

      expect(getWsEventsUrl()).toBe("wss://chat.example.com/api/v1/ws");
    });

    it("reverts to the build-time default after clearing the override", () => {
      saveBackendUrlOverride("https://chat.example.com");
      clearBackendUrlOverride();

      expect(getApiBaseUrl()).toBe("http://localhost:8000");
      expect(getWsEventsUrl()).toBe("ws://localhost:8000/api/v1/ws");
    });
  });
});
