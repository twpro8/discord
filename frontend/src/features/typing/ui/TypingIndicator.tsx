/**
 * Renders "who's typing" for a chat. Takes resolved display names rather
 * than user ids — kept generic over an arbitrary list (not DM-specific)
 * since the backend already supports group chats even though only DMs
 * have a chat view today.
 */
export function TypingIndicator({ names }: { names: string[] }) {
  if (names.length === 0) return null;

  const label =
    names.length === 1
      ? `${names[0]} is typing…`
      : names.length === 2
        ? `${names[0]} and ${names[1]} are typing…`
        : `${names.length} people are typing…`;

  return (
    <p
      role="status"
      aria-live="polite"
      className="h-5 shrink-0 px-4 text-xs text-muted-foreground"
    >
      {label}
    </p>
  );
}
