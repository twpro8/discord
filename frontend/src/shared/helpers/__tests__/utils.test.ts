import { cn, timeAgo } from "../utils";

describe("cn", () => {
  it("merges Tailwind classes, resolving conflicts", () => {
    expect(cn("px-4", "px-2")).toBe("px-2");
  });

  it("handles conditional classes via clsx", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });

  it("returns empty string for no inputs", () => {
    expect(cn()).toBe("");
  });
});

describe("timeAgo", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-07-27T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns "just now" for dates within 60 seconds', () => {
    expect(timeAgo("2026-07-27T12:00:30Z")).toBe("just now");
  });

  it('returns "5m ago" for 5 minutes ago', () => {
    expect(timeAgo("2026-07-27T11:55:00Z")).toBe("5m ago");
  });

  it('returns "2h ago" for 2 hours ago', () => {
    expect(timeAgo("2026-07-27T10:00:00Z")).toBe("2h ago");
  });

  it('returns "3d ago" for 3 days ago', () => {
    expect(timeAgo("2026-07-24T12:00:00Z")).toBe("3d ago");
  });

  it("returns a formatted date for dates older than 7 days", () => {
    const result = timeAgo("2026-07-01T12:00:00Z");
    expect(result).toBe("7/1/2026");
  });
});
