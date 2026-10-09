import { NextRequest, NextResponse } from "next/server";
import { resolveUserId } from "../../../_utils/user-identity";

const API_URL =
  process.env.NODE_ENV === "production"
    ? "http://clisonix-api:8000"
    : "http://127.0.0.1:8000";

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const userId = await resolveUserId(request);

  try {
    const res = await fetch(`${API_URL}/api/user/data-sources/${id}`, {
      method: "DELETE",
      headers: { Accept: "application/json", "X-User-ID": userId },
    });

    if (res.ok) {
      const data = await res.json().catch(() => ({ ok: true, deleted: id }));
      return NextResponse.json(data, { status: 200 });
    }

    const error = await res.json().catch(() => null);
    return NextResponse.json(
      {
        error:
          error?.detail ||
          error?.error ||
          "Failed to delete data source upstream",
        upstreamStatus: res.status,
      },
      { status: res.status >= 500 ? 503 : res.status },
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "User data source delete upstream is unavailable",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 503 },
    );
  }
}
