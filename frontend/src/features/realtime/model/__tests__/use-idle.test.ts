import { act, renderHook } from "@testing-library/react";

import { useIdle } from "../use-idle";

describe("useIdle", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("starts as not idle", () => {
    const { result } = renderHook(() => useIdle(5_000));
    expect(result.current).toBe(false);
  });

  it("becomes idle once the threshold elapses with no activity", () => {
    const { result } = renderHook(() => useIdle(5_000));

    act(() => {
      vi.advanceTimersByTime(6_000);
    });

    expect(result.current).toBe(true);
  });

  it("stays active when activity happens before the threshold elapses", () => {
    const { result } = renderHook(() => useIdle(5_000));

    act(() => {
      vi.advanceTimersByTime(3_000);
      window.dispatchEvent(new Event("mousemove"));
      vi.advanceTimersByTime(3_000);
    });

    expect(result.current).toBe(false);
  });

  it("returns to active on new activity after having gone idle", () => {
    const { result } = renderHook(() => useIdle(5_000));

    act(() => {
      vi.advanceTimersByTime(6_000);
    });
    expect(result.current).toBe(true);

    act(() => {
      window.dispatchEvent(new Event("keydown"));
    });
    expect(result.current).toBe(false);
  });

  it("treats the tab becoming visible again as activity", () => {
    const { result } = renderHook(() => useIdle(5_000));

    act(() => {
      vi.advanceTimersByTime(6_000);
    });
    expect(result.current).toBe(true);

    act(() => {
      vi.spyOn(document, "visibilityState", "get").mockReturnValue("visible");
      document.dispatchEvent(new Event("visibilitychange"));
    });
    expect(result.current).toBe(false);
  });
});
