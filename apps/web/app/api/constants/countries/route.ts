import { apiSuccess } from "@/lib/api/response";

function getRegionCodes(): string[] {
  const regionCodes: string[] = [];

  for (let first = 65; first <= 90; first += 1) {
    for (let second = 65; second <= 90; second += 1) {
      regionCodes.push(`${String.fromCharCode(first)}${String.fromCharCode(second)}`);
    }
  }

  return regionCodes;
}

export async function GET() {
  const displayNames = new Intl.DisplayNames(["en"], { type: "region" });
  const countries = getRegionCodes()
    .map((code) => ({
      code,
      name: displayNames.of(code) || code,
    }))
    .filter((entry) => entry.name !== entry.code)
    .sort((left, right) => left.name.localeCompare(right.name));

  return apiSuccess({ countries });
}
