type ApprovalChannel = "sms" | "email";

type ApprovalRecord = {
  identifier: string;
  channel: ApprovalChannel;
  code: string;
  requestId: string;
  createdAt: number;
  expiresAt: number;
  attempts: number;
};

const APPROVAL_TTL_MS = 10 * 60 * 1000;
const MAX_ATTEMPTS = 5;

type StoreShape = Map<string, ApprovalRecord>;

function getStore(): StoreShape {
  const globalKey = "__clisonix_internal_approval_store__";
  const root = globalThis as unknown as Record<string, StoreShape | undefined>;
  if (!root[globalKey]) {
    root[globalKey] = new Map<string, ApprovalRecord>();
  }
  return root[globalKey]!;
}

function normalizeIdentifier(value: string): string {
  return value.trim().toLowerCase();
}

function maskIdentifier(identifier: string, channel: ApprovalChannel): string {
  if (channel === "email") {
    const [name, domain] = identifier.split("@");
    if (!name || !domain) return "***";
    const visible = name.slice(0, 2);
    return `${visible}${"*".repeat(Math.max(1, name.length - 2))}@${domain}`;
  }

  const tail = identifier.slice(-3);
  return `${"*".repeat(Math.max(4, identifier.length - 3))}${tail}`;
}

function generateCode(): string {
  const raw = globalThis.crypto?.getRandomValues?.(new Uint32Array(1))[0];
  if (typeof raw === "number") {
    return String(100000 + (raw % 900000));
  }
  return Math.floor(100000 + Math.random() * 900000).toString();
}

export function requestInternalApproval(identifierRaw: string, channel: ApprovalChannel) {
  const identifier = normalizeIdentifier(identifierRaw);
  const now = Date.now();
  const code = generateCode();
  const requestId = `${now}-${Math.random().toString(36).slice(2, 8)}`;

  const record: ApprovalRecord = {
    identifier,
    channel,
    code,
    requestId,
    createdAt: now,
    expiresAt: now + APPROVAL_TTL_MS,
    attempts: 0,
  };

  getStore().set(identifier, record);

  return {
    requestId,
    expiresInSeconds: Math.floor(APPROVAL_TTL_MS / 1000),
    maskedDestination: maskIdentifier(identifier, channel),
    devCode: process.env.NODE_ENV !== "production" ? code : undefined,
  };
}

export function verifyInternalApproval(identifierRaw: string, codeRaw: string): boolean {
  const identifier = normalizeIdentifier(identifierRaw);
  const code = codeRaw.trim();
  const store = getStore();
  const record = store.get(identifier);

  if (!record) return false;
  if (Date.now() > record.expiresAt) {
    store.delete(identifier);
    return false;
  }

  record.attempts += 1;
  if (record.attempts > MAX_ATTEMPTS) {
    store.delete(identifier);
    return false;
  }

  if (record.code !== code) {
    store.set(identifier, record);
    return false;
  }

  store.delete(identifier);
  return true;
}

export function inferChannel(identifierRaw: string): ApprovalChannel {
  return identifierRaw.includes("@") ? "email" : "sms";
}
