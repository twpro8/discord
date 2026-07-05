import type { ApiError } from "@/api/errors.ts";

function extractErrorMessage(err: ApiError): string {
    const detail = err.body?.detail

    if (Array.isArray(detail)) {
        return detail[0]?.msg ?? "Something went wrong."
    }

    return detail ?? err.message
}

export const handleError = function (
    this: (msg: string) => void,
    err: any,
) {
    this(extractErrorMessage(err))
}

export const getInitials = (name: string): string => {
    return name
        .split(" ")
        .slice(0, 2)
        .map((word) => word[0])
        .join("")
        .toUpperCase()
}

const COLORS = [
    "#7287fd",
    "#74c7ec",
    "#89dceb",
    "#a6e3a1",
    "#94e2d5",
    "#cba6f7",
    "#f5c2e7",
    "#fab387",
    "#f9e2af",
    "#89b4fa",
];

export function colorFromId(id: string): string {
    const sum = id.split("").reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
    return COLORS[sum % COLORS.length];
}
