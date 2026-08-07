import {
  applyThemePreference,
  defaultDarkPalette,
  defaultLightPalette,
  formatResolvedTheme,
  formatThemePreference,
  getThemePalette,
  parseThemePreference,
  readThemePreference,
  saveThemePreference,
  type ThemePalette,
} from "../theme";

const palette: ThemePalette = {
  canvas: "#111318",
  surface: "#181b22",
  surfaceRaised: "#20242d",
  surfaceHover: "#292e39",
  border: "#2b303a",
  borderStrong: "#414858",
  textPrimary: "#f3f5f7",
  textSecondary: "#aab1bf",
  textTertiary: "#737b8b",
  textDisabled: "#555d6b",
  accent: "#7c8cff",
  accentHover: "#93a0ff",
  accentPressed: "#6575ed",
  accentSubtle: "#20264a",
  onAccent: "#ffffff",
  success: "#4ecb8d",
  warning: "#eab85d",
  danger: "#f17878",
  info: "#6eaeff",
  overlay: "rgb(5 7 11 / 64%)",
};

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

describe("theme preferences", () => {
  beforeEach(() => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: createStorage(),
    });
    window.localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    document.documentElement.removeAttribute("style");
  });

  it("returns a system preference when local storage is empty", () => {
    expect(readThemePreference()).toEqual({ mode: "system" });
  });

  it("rejects custom palettes with missing semantic tokens", () => {
    expect(
      parseThemePreference(
        JSON.stringify({ mode: "custom", name: "Incomplete", palette: {} }),
      ),
    ).toEqual({
      ok: false,
      error:
        "Palette must include every supported semantic color exactly once.",
    });
  });

  it("stores and applies a validated custom palette", () => {
    const preference = { mode: "custom", name: "Midnight", palette } as const;

    saveThemePreference(preference);

    expect(readThemePreference()).toEqual(preference);
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(
      document.documentElement.style.getPropertyValue("--color-accent"),
    ).toBe("#7c8cff");
  });

  it("removes a custom palette when applying a preset", () => {
    applyThemePreference({ mode: "custom", name: "Midnight", palette });
    applyThemePreference({ mode: "preset", preset: "light" });

    expect(document.documentElement.dataset.theme).toBe("light");
    expect(
      document.documentElement.style.getPropertyValue("--color-accent"),
    ).toBe("");
  });

  it("round-trips accepted JSON", () => {
    const source = formatThemePreference({
      mode: "custom",
      name: "Midnight",
      palette,
    });

    expect(parseThemePreference(source)).toEqual({
      ok: true,
      value: { mode: "custom", name: "Midnight", palette },
    });
  });

  it("accepts a custom palette without an optional display name", () => {
    expect(
      parseThemePreference(JSON.stringify({ mode: "custom", palette })),
    ).toEqual({
      ok: true,
      value: { mode: "custom", name: "Custom theme", palette },
    });
  });

  it("rejects undocumented fields in a custom palette file", () => {
    expect(
      parseThemePreference(
        JSON.stringify({ mode: "custom", preset: "dark", palette }),
      ),
    ).toEqual({
      ok: false,
      error: "Custom themes may contain only mode, name, and palette.",
    });
  });

  it("exposes complete palettes for each built-in theme", () => {
    expect(getThemePalette({ mode: "preset", preset: "dark" })).toEqual(
      defaultDarkPalette,
    );
    expect(getThemePalette({ mode: "preset", preset: "light" })).toEqual(
      defaultLightPalette,
    );
    const exportedDefault = formatResolvedTheme({
      mode: "preset",
      preset: "dark",
    });
    expect(parseThemePreference(exportedDefault)).toEqual({
      ok: true,
      value: {
        mode: "custom",
        name: "Lumiere dark",
        palette: defaultDarkPalette,
      },
    });
  });
});
