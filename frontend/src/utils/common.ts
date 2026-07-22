import { isApiError } from "@/api/errors.ts";

type ErrorBody = { detail?: unknown; msg?: unknown };

function isErrorBody(value: unknown): value is ErrorBody {
    return typeof value === "object" && value !== null;
}

export function getErrorMessage(error: unknown): string {
    if (!isApiError(error)) {
        return error instanceof Error ? error.message : "Something went wrong.";
    }

    const detail = isErrorBody(error.body) ? error.body.detail : undefined;

    if (Array.isArray(detail)) {
        const firstError = detail[0];
        if (isErrorBody(firstError) && typeof firstError.msg === "string") {
            return firstError.msg;
        }
    }

    return typeof detail === "string" ? detail : error.message;
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
