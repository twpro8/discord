export function formatRelativeTime(isoString: string): string {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHours = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSec < 60) return "now";
    if (diffMin < 60) return `${diffMin}m`;
    if (diffHours < 24) return `${diffHours}h`;

    const isSameDay = (a: Date, b: Date) =>
        a.getFullYear() === b.getFullYear() &&
        a.getMonth() === b.getMonth() &&
        a.getDate() === b.getDate();

    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);

    if (isSameDay(date, yesterday)) return "yesterday";

    if (diffDays < 7) {
        return date.toLocaleDateString(undefined, { weekday: "short" });
    }

    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString(undefined, { day: "numeric", month: "short" });
    }

    return date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
