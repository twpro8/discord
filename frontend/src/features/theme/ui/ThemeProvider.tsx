// react
import { useEffect } from "react";

// relative
import { refreshSystemTheme } from "../model/theme";

/** Keeps a system theme preference aligned with operating system changes. */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: light)");
    mediaQuery.addEventListener("change", refreshSystemTheme);
    return () => mediaQuery.removeEventListener("change", refreshSystemTheme);
  }, []);

  return children;
}
