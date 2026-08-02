// third party
import axios from "axios";

const UNEXPECTED_ERROR_MESSAGE = "Unexpected error";

/** Error response shape returned by the backend API. */
export interface ApiError {
  detail: string;
}

/** Extracts a human-readable error message from an unknown error value. */
export function getApiError(error: unknown): string {
  if (axios.isAxiosError<ApiError>(error)) {
    return error.response?.data.detail ?? error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return UNEXPECTED_ERROR_MESSAGE;
}
