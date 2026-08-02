import axios from "axios";

import { getApiError } from "../errors";

describe("getApiError", () => {
  it("returns the detail from an Axios error response", () => {
    const error = new axios.AxiosError(
      "Request failed",
      "ERR_BAD_REQUEST",
      undefined,
      undefined,
      { status: 400, data: { detail: "Invalid credentials" } } as any,
    );

    expect(getApiError(error)).toBe("Invalid credentials");
  });

  it("falls back to error message when Axios response has no detail", () => {
    const error = new axios.AxiosError("Network Error");

    expect(getApiError(error)).toBe("Network Error");
  });

  it("returns the message for a standard Error", () => {
    expect(getApiError(new Error("Something went wrong"))).toBe(
      "Something went wrong",
    );
  });

  it('returns "Unexpected error" for unknown input', () => {
    expect(getApiError("string")).toBe("Unexpected error");
    expect(getApiError(null)).toBe("Unexpected error");
    expect(getApiError(undefined)).toBe("Unexpected error");
  });
});
