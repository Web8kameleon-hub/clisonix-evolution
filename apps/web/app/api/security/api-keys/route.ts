import { randomBytes, createHash } from "crypto";
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";

interface StoredApiKey {
  id: string;
  userId: string;
  name: string;
  prefix: string;
  hash: string;
  createdAt: string;
  lastUsed?: string;
  revokedAt?: string;
}

const STORAGE_FILE_PATH = path.join(
  process.cwd(),
  "data",
  "security",
  "api-keys.json",
);

interface StorageShape {
  keys: StoredApiKey[];
}

async function readStorage(): Promise<StorageShape> {
  try {
    const raw = await readFile(STORAGE_FILE_PATH, "utf8");
    const parsed = JSON.parse(raw) as StorageShape;
    return {
      keys: Array.isArray(parsed.keys) ? parsed.keys : [],
    };
  } catch {
    return { keys: [] };
  }
}

async function writeStorage(data: StorageShape): Promise<void> {
  await mkdir(path.dirname(STORAGE_FILE_PATH), { recursive: true });
  await writeFile(STORAGE_FILE_PATH, JSON.stringify(data, null, 2), "utf8");
}

function hashKey(rawKey: string): string {
  return createHash("sha256").update(rawKey).digest("hex");
}

function maskKey(rawKey: string): string {
  return `${rawKey.slice(0, 12)}${"*".repeat(Math.max(rawKey.length - 12, 0))}`;
}

function buildRawKey(): string {
  return `sk_live_${randomBytes(24).toString("hex")}`;
}

export async function GET() {
  const user = await currentUser();
  if (!user) {
    return apiError("UNAUTHORIZED", "Authentication required", {
      status: 401,
    });
  }

  const storage = await readStorage();
  const keys = storage.keys
    .filter((entry) => entry.userId === user.id)
    .filter((entry) => !entry.revokedAt)
    .map((entry) => ({
      id: entry.id,
      name: entry.name,
      key: `${entry.prefix}${"*".repeat(24)}`,
      createdAt: entry.createdAt,
      lastUsed: entry.lastUsed,
    }));

  return apiSuccess({ keys });
}

export async function POST(request: Request) {
  const user = await currentUser();
  if (!user) {
    return apiError("UNAUTHORIZED", "Authentication required", {
      status: 401,
    });
  }

  const body = await request.json().catch(() => ({}));
  const name = String(body?.name || "").trim();
  if (!name) {
    return apiError("VALIDATION_ERROR", "API key name is required", {
      status: 400,
    });
  }

  const rawKey = buildRawKey();
  const now = new Date().toISOString();
  const id = `key_${randomBytes(8).toString("hex")}`;
  const entry: StoredApiKey = {
    id,
    userId: user.id,
    name,
    prefix: rawKey.slice(0, 12),
    hash: hashKey(rawKey),
    createdAt: now,
  };

  const storage = await readStorage();
  storage.keys.push(entry);
  await writeStorage(storage);

  return apiSuccess({
    key: {
      id,
      name,
      key: rawKey,
      maskedKey: maskKey(rawKey),
      createdAt: now,
    },
  });
}

export async function DELETE(request: Request) {
  const user = await currentUser();
  if (!user) {
    return apiError("UNAUTHORIZED", "Authentication required", {
      status: 401,
    });
  }

  const body = await request.json().catch(() => ({}));
  const keyId = String(body?.keyId || "").trim();
  if (!keyId) {
    return apiError("VALIDATION_ERROR", "Key ID is required", {
      status: 400,
    });
  }

  const storage = await readStorage();
  const matchingUserEntries = storage.keys.filter((entry) => entry.userId === user.id);
  const hasKey = matchingUserEntries.some((entry) => entry.id === keyId && !entry.revokedAt);

  if (!hasKey) {
    return apiError("NOT_FOUND", "API key not found", {
      status: 404,
    });
  }

  storage.keys = storage.keys.map((entry) =>
    entry.id === keyId
      ? {
          ...entry,
          revokedAt: new Date().toISOString(),
        }
      : entry,
  );
  await writeStorage(storage);

  return apiSuccess({
    revoked: true,
    keyId,
  });
}
