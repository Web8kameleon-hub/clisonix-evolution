export function normalizeSseLikeText(raw: string): string {
  if (!raw) return raw;

  let current = raw.includes("\\n") ? raw.replace(/\\r\\n|\\n/g, "\n") : raw;

  for (let pass = 0; pass < 3; pass++) {
    if (!current.includes("data:")) break;

    const collected: string[] = [];
    const events = current.split(/\r?\n\r?\n/);

    for (const event of events) {
      const lines = event.split(/\r?\n/);
      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line || !line.startsWith("data:")) continue;

        const payload = line.slice(5).trim();
        if (!payload || payload === "[DONE]") continue;

        try {
          const parsed = JSON.parse(payload);
          if (typeof parsed?.chunk === "string") {
            collected.push(parsed.chunk);
            continue;
          }
          if (typeof parsed?.text === "string") {
            collected.push(parsed.text);
            continue;
          }
          if (typeof parsed?.response === "string") {
            collected.push(parsed.response);
            continue;
          }
          if (typeof parsed?.answer === "string") {
            collected.push(parsed.answer);
            continue;
          }
        } catch {
          collected.push(payload);
        }
      }
    }

    if (!collected.length) break;
    const next = collected.join("");
    if (next === current) break;
    current = next;
  }

  return current;
}

export function extractChunkFromPayload(payload: string): string | null {
  if (!payload) return null;
  if (payload === "[DONE]") return null;

  const normalizedPayload = payload.startsWith("data:")
    ? payload.slice(payload.indexOf("data:") + 5).trim()
    : payload;

  try {
    const parsed = JSON.parse(normalizedPayload);
    if (typeof parsed?.chunk === "string") return parsed.chunk;
    if (typeof parsed?.text === "string") return parsed.text;
    if (typeof parsed?.response === "string") return parsed.response;
    if (typeof parsed?.answer === "string") return parsed.answer;
    return null;
  } catch {
    const chunkPrefix = '{"chunk":';
    const textPrefix = '{"text":';

    if (
      normalizedPayload.startsWith(chunkPrefix) ||
      normalizedPayload.startsWith(textPrefix)
    ) {
      const rawValue = normalizedPayload
        .slice(normalizedPayload.indexOf(":") + 1)
        .trim();
      const cleaned = rawValue
        .replace(/^"/, "")
        .replace(/"\}?\s*$/, "")
        .replace(/\\n/g, "\n")
        .replace(/\\"/g, '"');
      return cleaned;
    }

    if (
      !normalizedPayload.startsWith("{") &&
      !normalizedPayload.startsWith("[")
    ) {
      return normalizedPayload;
    }

    const chunkMatches = normalizedPayload.match(
      /"chunk"\s*:\s*"((?:\\.|[^"\\])*)"/g,
    );
    if (chunkMatches && chunkMatches.length > 0) {
      const merged = chunkMatches
        .map((match) => {
          const inner = match.replace(/^.*?:\s*"/, "").replace(/"\s*$/, "");
          return inner
            .replace(/\\n/g, "\n")
            .replace(/\\r/g, "\r")
            .replace(/\\t/g, "\t")
            .replace(/\\"/g, '"')
            .replace(/\\\\/g, "\\");
        })
        .join("");
      if (merged.trim()) return merged;
    }

    return null;
  }
}
