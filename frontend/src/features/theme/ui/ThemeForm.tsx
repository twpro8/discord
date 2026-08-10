// react
import { useRef, useState } from "react";

// third party
import { Copy } from "lucide-react";
import { toast } from "sonner";

// shared
import { Button } from "@/shared/ui/button";
import { Label } from "@/shared/ui/label";

// relative
import {
  formatResolvedTheme,
  formatThemePreference,
  getThemePalette,
  isThemeOptionActive,
  parseThemePreference,
  readThemePreference,
  saveThemePreference,
  type ThemePreference,
} from "../model/theme";

type ThemeOption = "system" | "dark" | "light";
type ImportMethod = "file" | "code";

/** Lets a user choose a built-in theme or apply a validated JSON palette. */
export function ThemeForm() {
  const [preference, setPreference] =
    useState<ThemePreference>(readThemePreference);
  const [source, setSource] = useState(() => formatThemePreference(preference));
  const [error, setError] = useState<string | null>(null);
  const [importMethod, setImportMethod] = useState<ImportMethod>("file");
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const parsedSource = parseThemePreference(source);
  const previewPreference = parsedSource.ok ? parsedSource.value : preference;
  const previewPalette = getThemePalette(previewPreference);

  function selectOption(option: ThemeOption) {
    const next: ThemePreference =
      option === "system"
        ? { mode: "system" }
        : { mode: "preset", preset: option };
    setPreference(next);
    setSource(formatThemePreference(next));
    setFileName(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    setError(null);
  }

  function applyJson(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!parsedSource.ok) {
      setError(parsedSource.error);
      return;
    }

    saveThemePreference(parsedSource.value);
    setPreference(parsedSource.value);
    setSource(formatThemePreference(parsedSource.value));
    setError(null);
    toast.success("Theme applied");
  }

  async function importFile(file: File | undefined) {
    if (!file) return;

    const nextSource = await file.text();
    setSource(nextSource);
    setFileName(file.name);
    setError(null);
  }

  async function copyResolvedTheme() {
    try {
      await navigator.clipboard.writeText(
        formatResolvedTheme(previewPreference),
      );
      toast.success("Palette JSON copied");
    } catch {
      toast.error("Unable to copy palette JSON");
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2 lg:items-start">
      <fieldset className="grid gap-3 lg:col-start-1 lg:row-start-1">
        <legend className="text-sm font-semibold text-foreground">
          Appearance
        </legend>
        <p className="text-sm text-muted-foreground">
          Choose a built-in theme or edit palette JSON, then preview it before
          applying.
        </p>
        <div className="grid gap-2 sm:grid-cols-3">
          {(["system", "dark", "light"] as const).map((option) => (
            <label
              key={option}
              className="flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-border bg-surface-raised px-3 text-sm text-foreground transition-colors hover:bg-surface-hover has-checked:border-primary has-checked:bg-accent-subtle"
            >
              <input
                type="radio"
                name="theme-option"
                value={option}
                checked={isThemeOptionActive(preference, option)}
                onChange={() => selectOption(option)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </fieldset>

      <div className="lg:col-start-2 lg:row-start-1">
        <ThemePreview palette={previewPalette} />
      </div>

      <details className="rounded-lg border border-border bg-surface-raised p-3 lg:col-start-2 lg:row-start-2">
        <summary className="cursor-pointer text-sm font-semibold text-foreground">
          View resolved palette JSON
        </summary>
        <p className="mt-2 text-xs text-muted-foreground">
          This is a complete, valid custom-theme JSON file. Copy it to use a
          built-in palette as a starting point.
        </p>
        <div className="mt-3 flex justify-end">
          <Button
            type="button"
            variant="outline"
            size="icon-sm"
            aria-label="Copy resolved palette JSON"
            title="Copy palette JSON"
            onClick={() => void copyResolvedTheme()}
          >
            <Copy />
          </Button>
        </div>
        <pre className="mt-2 max-h-40 overflow-auto rounded-md bg-canvas p-3 font-mono text-xs text-foreground">
          {formatResolvedTheme(previewPreference)}
        </pre>
      </details>

      <form
        onSubmit={applyJson}
        className="grid gap-3 lg:col-start-1 lg:row-start-2"
      >
        <fieldset className="grid gap-3">
          <legend className="text-sm font-semibold text-foreground">
            Import custom palette
          </legend>
          <div className="grid grid-cols-2 rounded-lg bg-muted p-1">
            <ImportMethodButton
              active={importMethod === "file"}
              onClick={() => setImportMethod("file")}
            >
              Upload file
            </ImportMethodButton>
            <ImportMethodButton
              active={importMethod === "code"}
              onClick={() => setImportMethod("code")}
            >
              Paste code
            </ImportMethodButton>
          </div>

          {importMethod === "file" ? (
            <div className="grid gap-2">
              <Label
                htmlFor="theme-file"
                className="w-fit cursor-pointer justify-self-center"
              >
                <span className="inline-flex h-10 items-center rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/80">
                  Choose JSON file
                </span>
              </Label>
              <input
                id="theme-file"
                type="file"
                accept="application/json,.json"
                className="sr-only"
                ref={fileInputRef}
                onChange={(event) => void importFile(event.target.files?.[0])}
              />
              <p className="text-xs text-muted-foreground">
                {fileName
                  ? `${fileName} is ready to preview.`
                  : "Choose a palette JSON file to preview it before applying."}
              </p>
            </div>
          ) : (
            <div className="grid gap-2">
              <Label htmlFor="theme-json">Palette JSON</Label>
              <textarea
                id="theme-json"
                value={source}
                onChange={(event) => setSource(event.target.value)}
                className="h-40 w-full resize-y rounded-lg border border-input bg-surface-raised p-3 font-mono text-xs text-foreground outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                aria-describedby="theme-json-help"
                aria-invalid={error ? true : undefined}
                spellCheck={false}
              />
            </div>
          )}
          <p id="theme-json-help" className="text-xs text-muted-foreground">
            Custom JSON supports only mode, an optional name, and palette. The
            resolved palette JSON above is a valid file to upload or paste.
          </p>
          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
        </fieldset>
        <Button type="submit">Apply theme</Button>
      </form>
    </div>
  );
}

function ImportMethodButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        active
          ? "rounded-md bg-background px-3 py-1.5 text-sm font-medium text-foreground shadow-sm"
          : "rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground"
      }
    >
      {children}
    </button>
  );
}

function ThemePreview({
  palette,
}: {
  palette: ReturnType<typeof getThemePalette>;
}) {
  return (
    <section
      aria-label="Theme preview"
      className="overflow-hidden rounded-lg border"
      style={{
        backgroundColor: palette.canvas,
        borderColor: palette.border,
        color: palette.textPrimary,
      }}
    >
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{
          backgroundColor: palette.surface,
          borderBottom: `1px solid ${palette.border}`,
        }}
      >
        <div>
          <p className="text-sm font-semibold">Theme preview</p>
          <p className="text-xs" style={{ color: palette.textSecondary }}>
            Changes are not saved until you apply them.
          </p>
        </div>
        <span
          className="rounded-md px-2 py-1 text-xs font-semibold"
          style={{
            backgroundColor: palette.accentSubtle,
            color: palette.accent,
          }}
        >
          Active
        </span>
      </div>
      <div className="grid gap-3 p-4 sm:grid-cols-2">
        <div
          className="rounded-md border p-3"
          style={{
            backgroundColor: palette.surfaceRaised,
            borderColor: palette.border,
          }}
        >
          <p className="text-sm font-medium">Conversation</p>
          <p className="mt-1 text-xs" style={{ color: palette.textSecondary }}>
            Your custom palette is shown here before it changes the app.
          </p>
        </div>
        <span
          className="min-h-10 rounded-md px-3 text-sm font-semibold"
          style={{ backgroundColor: palette.accent, color: palette.onAccent }}
        >
          Primary action
        </span>
      </div>
    </section>
  );
}
