import { apiSuccess } from "@/lib/api/response";

interface NotificationCategory {
  id: string;
  label: string;
  description: string;
  defaultEnabled: boolean;
}

function parseCategories(): NotificationCategory[] {
  const rawConfig = process.env.ACCOUNT_NOTIFICATION_CATEGORIES_JSON;
  if (!rawConfig) {
    return [];
  }

  try {
    const parsed = JSON.parse(rawConfig);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .map((entry) => ({
        id: String(entry?.id || "").trim(),
        label: String(entry?.label || "").trim(),
        description: String(entry?.description || "").trim(),
        defaultEnabled: Boolean(entry?.defaultEnabled),
      }))
      .filter((entry) => entry.id && entry.label);
  } catch {
    return [];
  }
}

export async function GET() {
  const categories = parseCategories();
  return apiSuccess({ categories });
}
