/** Human-readable message for a rejected camera `getUserMedia()` call —
 * the mid-call counterpart of microphoneErrorMessage (the mic is granted
 * at call start, the camera only when the user opts into video). */
export function cameraErrorMessage(error: unknown): string {
  if (error instanceof DOMException) {
    if (
      error.name === "NotAllowedError" ||
      error.name === "PermissionDeniedError"
    ) {
      return "Camera access was denied. Allow camera access to share video.";
    }
    if (
      error.name === "NotFoundError" ||
      error.name === "DevicesNotFoundError"
    ) {
      return "No camera was found on this device.";
    }
  }
  return "Couldn't access your camera.";
}

/** Human-readable message for a rejected `getDisplayMedia()` call.
 * "NotAllowedError" covers both the user choosing to cancel the picker
 * and the browser refusing screen capture entirely. */
export function screenShareErrorMessage(error: unknown): string {
  if (error instanceof DOMException) {
    if (
      error.name === "NotAllowedError" ||
      error.name === "PermissionDeniedError"
    ) {
      return "Screen sharing was canceled.";
    }
    if (
      error.name === "NotReadableError" ||
      error.name === "AbortError" ||
      error.name === "NotSupportedError"
    ) {
      return "Couldn't start screen sharing — try a different source.";
    }
  }
  return "Couldn't start screen sharing.";
}
