import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    success: true,
    postman: {
      connected: false,
      status: "publish_only",
      message:
        "Postman is kept only for public publishing/export. Runtime sync is disabled.",
    },
    kitchen: {
      linked: false,
      message: "Kitchen no longer syncs Postman collections at runtime.",
    },
    timestamp: new Date().toISOString(),
  });
}
