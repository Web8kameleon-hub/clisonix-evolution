import { apiSuccess } from "@/lib/api/response";

function parseThemeConfig() {
  const rawConfig = process.env.ACCOUNT_THEMES_JSON;
  if (!rawConfig) {
    return [] as Array<{ id: string; name: string }>;
  }

  try {
    const parsed = JSON.parse(rawConfig);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .map((entry) => ({
        id: String(entry?.id || "").trim(),
        name: String(entry?.name || "").trim(),
      }))
      .filter((entry) => entry.id.length > 0 && entry.name.length > 0);
  } catch {
    return [];
  }
}

export async function GET() {
  const themes = parseThemeConfig();
  return apiSuccess({ themes });
}
