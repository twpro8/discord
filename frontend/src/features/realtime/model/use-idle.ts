// react
import { useEffect, useRef, useState } from "react";

const DEFAULT_IDLE_THRESHOLD_MS = 5 * 60 * 1000;
const CHECK_INTERVAL_MS = 1_000;
const ACTIVITY_EVENTS = [
  "mousemove",
  "keydown",
  "scroll",
  "touchstart",
] as const;

/**
 * Tracks whether the user has been inactive for longer than the idle
 * threshold — the sole source of the client-reported `idle` flag sent in
 * heartbeats (drives the Away status). The server never infers idleness
 * itself, it only relays whatever this hook last reported.
 */
export function useIdle(
  thresholdMs: number = DEFAULT_IDLE_THRESHOLD_MS,
): boolean {
  const [idle, setIdle] = useState(false);
  const lastActivityRef = useRef(Date.now());

  useEffect(() => {
    const markActive = () => {
      lastActivityRef.current = Date.now();
      setIdle(false);
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") markActive();
    };

    for (const eventName of ACTIVITY_EVENTS) {
      window.addEventListener(eventName, markActive, { passive: true });
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const interval = window.setInterval(() => {
      if (Date.now() - lastActivityRef.current >= thresholdMs) {
        setIdle(true);
      }
    }, CHECK_INTERVAL_MS);

    return () => {
      for (const eventName of ACTIVITY_EVENTS) {
        window.removeEventListener(eventName, markActive);
      }
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.clearInterval(interval);
    };
  }, [thresholdMs]);

  return idle;
}
