// react
import { useSyncExternalStore } from "react";

function getSnapshot(query: string) {
  if (typeof window === "undefined") return false;
  return window.matchMedia(query).matches;
}

function subscribe(query: string, onChange: () => void) {
  if (typeof window === "undefined") return () => {};
  const mql = window.matchMedia(query);
  mql.addEventListener("change", onChange);
  return () => mql.removeEventListener("change", onChange);
}

/** Subscribes to a CSS media query, re-rendering when its match state changes. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => subscribe(query, onChange),
    () => getSnapshot(query),
    () => false,
  );
}
