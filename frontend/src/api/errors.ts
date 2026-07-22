export class ApiError extends Error {
    readonly status: number
    readonly body: unknown

    constructor(status: number, body: unknown) {
        super(`API Error: ${status}`)
        this.name = "ApiError"
        this.status = status
        this.body = body
    }
}

export function isApiError(error: unknown): error is ApiError {
    return error instanceof ApiError;
}
