import { apiSuccess } from "@/lib/api/response";

function buildOffsetLabel(timeZone: string): string {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    timeZoneName: "shortOffset",
  });

  const part = formatter
    .formatToParts(new Date())
    .find((item) => item.type === "timeZoneName")?.value;

  return part || "UTC";
}

export async function GET() {
  const timezones = Intl.supportedValuesOf("timeZone").map((timeZone) => ({
    id: timeZone,
    label: timeZone.replace(/_/g, " "),
    offset: buildOffsetLabel(timeZone),
  }));

  return apiSuccess({ timezones });
}
