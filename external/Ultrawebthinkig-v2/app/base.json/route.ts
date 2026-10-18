import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

async function readBaseJson(): Promise<string> {
  const candidates = [
    path.join(process.cwd(), "base.json"),
    path.join(process.cwd(), "..", "base.json"),
  ];
  for (const p of candidates) {
    try {
      return await fs.readFile(p, "utf-8");
    } catch {}
  }
  throw new Error("base.json not found");
}

export async function GET() {
  try {
    const data = await readBaseJson();
    return new NextResponse(data, { headers: { "content-type": "application/json" } });
  } catch (e) {
    return NextResponse.json(
      { error: "base.json not found or invalid" },
      { status: 500 }
    );
  }
}
