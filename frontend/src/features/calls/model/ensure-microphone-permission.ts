// third party
import { isTauri } from "@tauri-apps/api/core";
import {
  checkMicrophonePermission,
  requestMicrophonePermission,
} from "tauri-plugin-macos-permissions-api";

/** WKWebView on macOS rejects getUserMedia before any TCC prompt can
 * appear unless the app-level microphone permission is already granted —
 * so request it via the plugin first (AVFoundation, which works even in
 * `tauri dev`, where the raw debug binary has no bundled Info.plist).
 * No-op outside macOS Tauri: browsers prompt on the getUserMedia call
 * itself, Windows WebView2 prompts natively, and on Linux the shell's
 * native permission-request handler grants media access. Throws a
 * NotAllowedError DOMException when the user denies so callers can
 * format it with microphoneErrorMessage. */
export async function ensureMicrophonePermission(): Promise<void> {
  if (!isTauri() || !navigator.platform.toLowerCase().includes("mac")) return;
  if (await checkMicrophonePermission()) return;
  await requestMicrophonePermission();
  if (!(await checkMicrophonePermission())) {
    throw new DOMException("denied", "NotAllowedError");
  }
}
