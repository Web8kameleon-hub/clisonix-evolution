import { apiError, apiSuccess } from "@/lib/api/response";

// Internal API URL - use localhost in dev, Docker container name in production
const isDev = process.env.NODE_ENV === "development";
const API_INTERNAL =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://clisonix-api:8000");

export async function GET() {
  try {
    const response = await fetch(`${API_INTERNAL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      return apiError(
        "UPSTREAM_STATUS_ERROR",
        "Main API health returned a non-200 status",
        {
          status: response.status,
          details: {
            upstream: `${API_INTERNAL}/health`,
            upstreamStatus: response.status,
          },
        },
      );
    }

    const data = await response.json();
    return apiSuccess(data, {
      meta: {
        upstream: `${API_INTERNAL}/health`,
      },
    });
  } catch (error) {
    return apiError(
      "UPSTREAM_UNAVAILABLE",
      "Failed to connect to Main API health endpoint",
      {
        status: 503,
        details: {
          upstream: `${API_INTERNAL}/health`,
          reason: String(error),
        },
      },
    );
  }
}
