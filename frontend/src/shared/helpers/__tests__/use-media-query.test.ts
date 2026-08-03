import { act, renderHook } from "@testing-library/react";

import { useMediaQuery } from "../use-media-query";

class FakeMediaQueryList {
  matches = false;
  media: string;
  private listeners = new Set<() => void>();

  constructor(media: string) {
    this.media = media;
  }

  addEventListener = (type: string, callback: () => void) => {
    if (type === "change") this.listeners.add(callback);
  };

  removeEventListener = (type: string, callback: () => void) => {
    if (type === "change") this.listeners.delete(callback);
  };

  setMatches(matches: boolean) {
    this.matches = matches;
    this.listeners.forEach((callback) => callback());
  }
}

/** Installs a query-singleton matchMedia stub, returning the live lists. */
function installMatchMedia(initial: Record<string, boolean> = {}) {
  const lists = new Map<string, FakeMediaQueryList>();
  vi.stubGlobal("matchMedia", (query: string) => {
    let list = lists.get(query);
    if (!list) {
      list = new FakeMediaQueryList(query);
      list.matches = initial[query] ?? false;
      lists.set(query, list);
    }
    return list as unknown as MediaQueryList;
  });
  return lists;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("useMediaQuery", () => {
  it("returns the initial match state", () => {
    installMatchMedia({ "(min-width: 1024px)": true });
    const { result } = renderHook(() => useMediaQuery("(min-width: 1024px)"));
    expect(result.current).toBe(true);
  });

  it("re-renders when the query match state changes", () => {
    const lists = installMatchMedia();
    const { result } = renderHook(() => useMediaQuery("(min-width: 1024px)"));
    expect(result.current).toBe(false);

    act(() => {
      lists.get("(min-width: 1024px)")?.setMatches(true);
    });
    expect(result.current).toBe(true);
  });
});
