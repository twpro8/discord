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
