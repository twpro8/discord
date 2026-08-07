/** A complete set of semantic color tokens used by the application. */
export type ThemePalette = {
  canvas: string;
  surface: string;
  surfaceRaised: string;
  surfaceHover: string;
  border: string;
  borderStrong: string;
  textPrimary: string;
  textSecondary: string;
  textTertiary: string;
  textDisabled: string;
  accent: string;
  accentHover: string;
  accentPressed: string;
  accentSubtle: string;
  onAccent: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  overlay: string;
};

/** A stored preference that resolves to the operating system theme. */
type SystemThemePreference = { mode: "system" };

/** A stored preference that uses one of Lumiere's built-in palettes. */
type PresetThemePreference = { mode: "preset"; preset: "dark" | "light" };

/** A stored preference containing a user-provided semantic palette. */
type CustomThemePreference = {
  mode: "custom";
  name: string;
  palette: ThemePalette;
};

/** The complete local theme preference format. */
export type ThemePreference =
  SystemThemePreference | PresetThemePreference | CustomThemePreference;

const STORAGE_KEY = "lumiere.theme-preference";
const COLOR_VALUE =
  /^(#[\da-fA-F]{3,4}|#[\da-fA-F]{6}|#[\da-fA-F]{8}|rgb\((?:\d{1,3}\s+){2}\d{1,3}(?:\s*\/\s*(?:0|1|0?\.\d+|\d{1,3}%))?\))$/;

const paletteVariables: Record<keyof ThemePalette, string> = {
  canvas: "--color-canvas",
  surface: "--color-surface",
  surfaceRaised: "--color-surface-raised",
  surfaceHover: "--color-surface-hover",
  border: "--color-border",
  borderStrong: "--color-border-strong",
  textPrimary: "--color-text-primary",
  textSecondary: "--color-text-secondary",
  textTertiary: "--color-text-tertiary",
  textDisabled: "--color-text-disabled",
  accent: "--color-accent",
  accentHover: "--color-accent-hover",
  accentPressed: "--color-accent-pressed",
  accentSubtle: "--color-accent-subtle",
  onAccent: "--color-on-accent",
  success: "--color-success",
  warning: "--color-warning",
  danger: "--color-danger",
  info: "--color-info",
  overlay: "--color-overlay",
};

const paletteKeys = Object.keys(paletteVariables) as Array<keyof ThemePalette>;

/** Lumiere's built-in dark palette, expressed in the same JSON shape as custom themes. */
export const defaultDarkPalette: ThemePalette = {
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

/** Lumiere's built-in light palette, including shared status colours. */
export const defaultLightPalette: ThemePalette = {
  canvas: "#f7f8fa",
  surface: "#ffffff",
  surfaceRaised: "#ffffff",
  surfaceHover: "#eef0f5",
  border: "#e1e4ea",
  borderStrong: "#c9cfda",
  textPrimary: "#1b1f27",
  textSecondary: "#5d6573",
  textTertiary: "#858c99",
  textDisabled: "#b0b5be",
  accent: "#5265d9",
  accentHover: "#4558cb",
  accentPressed: "#3c4db5",
  accentSubtle: "#e9ecff",
  onAccent: "#ffffff",
  success: "#4ecb8d",
  warning: "#eab85d",
  danger: "#f17878",
  info: "#6eaeff",
  overlay: "rgb(20 25 35 / 40%)",
};

/** Returns the system or dark palette when no valid preference has been stored. */
export function readThemePreference(): ThemePreference {
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (!stored) return { mode: "system" };

  const result = parseThemePreference(stored);
  return result.ok ? result.value : { mode: "system" };
}

/** Parses and validates a JSON theme preference before it reaches the document. */
export function parseThemePreference(
  source: string,
): { ok: true; value: ThemePreference } | { ok: false; error: string } {
  let value: unknown;
  try {
    value = JSON.parse(source);
  } catch {
    return { ok: false, error: "Theme JSON is invalid." };
  }

  if (!isRecord(value) || typeof value.mode !== "string") {
    return { ok: false, error: "Theme JSON must include a mode." };
  }

  if (value.mode === "system" && Object.keys(value).length === 1) {
    return { ok: true, value: { mode: "system" } };
  }

  if (
    value.mode === "preset" &&
    (value.preset === "dark" || value.preset === "light") &&
    Object.keys(value).length === 2
  ) {
    return { ok: true, value: { mode: "preset", preset: value.preset } };
  }

  if (
    value.mode === "custom" &&
    Object.keys(value).some(
      (key) => key !== "mode" && key !== "name" && key !== "palette",
    )
  ) {
    return {
      ok: false,
      error: "Custom themes may contain only mode, name, and palette.",
    };
  }

  if (value.mode !== "custom" || !("palette" in value)) {
    return {
      ok: false,
      error: "Theme mode must be system, preset, or custom.",
    };
  }

  if ("name" in value && typeof value.name !== "string") {
    return { ok: false, error: "Custom theme names must be text." };
  }

  const name =
    typeof value.name === "string" ? value.name.trim() : "Custom theme";
  if (name.length < 1 || name.length > 64) {
    return { ok: false, error: "Custom theme names must be 1–64 characters." };
  }

  const palette = parsePalette(value.palette);
  if (!palette.ok) return palette;

  return {
    ok: true,
    value: { mode: "custom", name, palette: palette.value },
  };
}

/** Serializes a preference in the JSON format accepted by the theme importer. */
export function formatThemePreference(preference: ThemePreference): string {
  return JSON.stringify(preference, null, 2);
}

/** Returns the fully resolved palette for a preference, including built-in themes. */
export function getThemePalette(preference: ThemePreference): ThemePalette {
  if (preference.mode === "custom") return preference.palette;
  if (preference.mode === "preset") {
    return preference.preset === "light"
      ? defaultLightPalette
      : defaultDarkPalette;
  }
  return getSystemTheme() === "light"
    ? defaultLightPalette
    : defaultDarkPalette;
}

/** Serializes a preference's resolved palette as a valid custom-theme import. */
export function formatResolvedTheme(preference: ThemePreference): string {
  return JSON.stringify(
    {
      mode: "custom",
      name:
        preference.mode === "custom"
          ? preference.name
          : preference.mode === "preset"
            ? `Lumiere ${preference.preset}`
            : "Lumiere system",
      palette: getThemePalette(preference),
    },
    null,
    2,
  );
}

/** Saves a validated preference locally and applies it immediately. */
export function saveThemePreference(preference: ThemePreference) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preference));
  applyThemePreference(preference);
}

/** Applies a preference's semantic tokens to the document root. */
export function applyThemePreference(preference: ThemePreference) {
  const root = document.documentElement;
  clearPaletteVariables(root);

  if (preference.mode === "custom") {
    root.dataset.theme = "dark";
    for (const key of paletteKeys) {
      root.style.setProperty(paletteVariables[key], preference.palette[key]);
    }
    return;
  }

  root.dataset.theme =
    preference.mode === "preset" ? preference.preset : getSystemTheme();
}

/** Applies the persisted local preference during application startup. */
export function initializeTheme() {
  applyThemePreference(readThemePreference());
}

/** Reapplies the saved preference after the operating system theme changes. */
export function refreshSystemTheme() {
  const preference = readThemePreference();
  if (preference.mode === "system") applyThemePreference(preference);
}

/** Reports whether a preference currently matches a selectable theme option. */
export function isThemeOptionActive(
  preference: ThemePreference,
  option: "system" | "dark" | "light",
) {
  return (
    (option === "system" && preference.mode === "system") ||
    (option !== "system" &&
      preference.mode === "preset" &&
      preference.preset === option)
  );
}

function parsePalette(
  value: unknown,
): { ok: true; value: ThemePalette } | { ok: false; error: string } {
  if (!isRecord(value)) {
    return { ok: false, error: "Custom themes must include a palette object." };
  }

  const keys = Object.keys(value);
  if (
    keys.length !== paletteKeys.length ||
    keys.some((key) => !paletteKeys.includes(key as keyof ThemePalette))
  ) {
    return {
      ok: false,
      error:
        "Palette must include every supported semantic color exactly once.",
    };
  }

  const palette = {} as ThemePalette;
  for (const key of paletteKeys) {
    const color = value[key];
    if (typeof color !== "string" || !COLOR_VALUE.test(color)) {
      return {
        ok: false,
        error: `${key} must be a hex color or a numeric rgb() color.`,
      };
    }
    palette[key] = color;
  }

  return { ok: true, value: palette };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function clearPaletteVariables(root: HTMLElement) {
  for (const variable of Object.values(paletteVariables)) {
    root.style.removeProperty(variable);
  }
}

function getSystemTheme(): "dark" | "light" {
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}
