import axios from 'axios'

const UNEXPECTED_ERROR_MESSAGE = 'Unexpected error'

export interface ApiError {
    detail: string
}

export function getApiError(error: unknown): string {
    if (axios.isAxiosError<ApiError>(error)) {
        return error.response?.data.detail ?? error.message
    }

    if (error instanceof Error) {
        return error.message
    }

    return UNEXPECTED_ERROR_MESSAGE
}