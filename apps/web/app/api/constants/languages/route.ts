import { apiSuccess } from "@/lib/api/response";
import { languageNames } from "@/lib/i18n";

export async function GET() {
  const languages = Object.entries(languageNames).map(([code, name]) => ({
    code,
    name,
  }));

  return apiSuccess({ languages });
}
