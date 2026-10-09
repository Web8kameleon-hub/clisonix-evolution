import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";

type NotificationPreferences = Record<string, boolean>;

interface StorageShape {
  preferences: Record<string, NotificationPreferences>;
}

const STORAGE_FILE_PATH = path.join(
  process.cwd(),
  "data",
  "user",
  "notification-preferences.json",
);

async function readStorage(): Promise<StorageShape> {
  try {
    const raw = await readFile(STORAGE_FILE_PATH, "utf8");
    const parsed = JSON.parse(raw) as StorageShape;
    return {
      preferences: parsed.preferences || {},
    };
  } catch {
    return { preferences: {} };
  }
}

async function writeStorage(data: StorageShape) {
  await mkdir(path.dirname(STORAGE_FILE_PATH), { recursive: true });
  await writeFile(STORAGE_FILE_PATH, JSON.stringify(data, null, 2), "utf8");
}

export async function GET() {
  const user = await currentUser();
  if (!user) {
    return apiError("UNAUTHORIZED", "Authentication required", {
      status: 401,
    });
  }

  const storage = await readStorage();
  const preferences = storage.preferences[user.id] || {};

  return apiSuccess({ preferences });
}

export async function PUT(request: Request) {
  const user = await currentUser();
  if (!user) {
    return apiError("UNAUTHORIZED", "Authentication required", {
      status: 401,
    });
  }

  const body = await request.json().catch(() => ({}));
  const preferences = body?.preferences as NotificationPreferences | undefined;

  if (!preferences || typeof preferences !== "object") {
    return apiError("VALIDATION_ERROR", "Preferences payload is required", {
      status: 400,
    });
  }

  const normalized: NotificationPreferences = Object.fromEntries(
    Object.entries(preferences).map(([key, value]) => [key, Boolean(value)]),
  );

  const storage = await readStorage();
  storage.preferences[user.id] = normalized;
  await writeStorage(storage);

  return apiSuccess({ preferences: normalized });
}
