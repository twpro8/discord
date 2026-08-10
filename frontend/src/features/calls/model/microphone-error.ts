/** Human-readable message for a rejected `getUserMedia()` call, shared
 * between the caller (use-start-call.ts) and callee (IncomingCallModal)
 * mic-permission paths. */
export function microphoneErrorMessage(error: unknown): string {
  if (error instanceof DOMException) {
    if (
      error.name === "NotAllowedError" ||
      error.name === "PermissionDeniedError"
    ) {
      return "Microphone access was denied. Allow microphone access to make calls.";
    }
    if (
      error.name === "NotFoundError" ||
      error.name === "DevicesNotFoundError"
    ) {
      return "No microphone was found on this device.";
    }
  }
  return "Couldn't access your microphone.";
}
