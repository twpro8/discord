export class ApiError extends Error {
    status: number
    body: any

    constructor(status: number, body: any) {
        super(`API Error: ${status}`)
        this.name = "ApiError"
        this.status = status
        this.body = body
    }
}
