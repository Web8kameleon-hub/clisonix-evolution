type ConversationMessage = { role: string; content: string };

type ExportArtifact = {
  fileName: string;
  mimeType: string;
  bytes: Uint8Array;
};

type LocalExportFormat = "pdf" | "docx" | "xlsx";

const encoder = new TextEncoder();

function concatBytes(parts: Uint8Array[]): Uint8Array {
  const result = new Uint8Array(parts.reduce((sum, part) => sum + part.length, 0));
  let offset = 0;
  for (const part of parts) {
    result.set(part, offset);
    offset += part.length;
  }
  return result;
}

function xmlEscape(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function u16(value: number): Uint8Array {
  return Uint8Array.of(value & 0xff, (value >>> 8) & 0xff);
}

function u32(value: number): Uint8Array {
  return Uint8Array.of(
    value & 0xff,
    (value >>> 8) & 0xff,
    (value >>> 16) & 0xff,
    (value >>> 24) & 0xff,
  );
}

function zip(files: Array<{ name: string; content: string }>): Uint8Array {
  const localParts: Uint8Array[] = [];
  const centralParts: Uint8Array[] = [];
  let offset = 0;

  for (const file of files) {
    const name = encoder.encode(file.name);
    const data = encoder.encode(file.content);
    const checksum = crc32(data);
    const local = concatBytes([
      u32(0x04034b50), u16(20), u16(0x0800), u16(0), u16(0), u16(0),
      u32(checksum), u32(data.length), u32(data.length), u16(name.length),
      u16(0), name, data,
    ]);
    localParts.push(local);

    centralParts.push(concatBytes([
      u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(0), u16(0),
      u16(0), u32(checksum), u32(data.length), u32(data.length),
      u16(name.length), u16(0), u16(0), u16(0), u16(0), u32(0),
      u32(offset), name,
    ]));
    offset += local.length;
  }

  const locals = concatBytes(localParts);
  const central = concatBytes(centralParts);
  const end = concatBytes([
    u32(0x06054b50), u16(0), u16(0), u16(files.length), u16(files.length),
    u32(central.length), u32(locals.length), u16(0),
  ]);
  return concatBytes([locals, central, end]);
}

function transcriptLines(messages: ConversationMessage[]): string[] {
  const lines = ["Curiosity Ocean", "Conversation export", ""];
  for (const message of messages) {
    const role = String(message.role || "user").toUpperCase();
    const content = String(message.content || "").replace(/\r\n/g, "\n").trim();
    if (!content) continue;
    lines.push(role);
    lines.push(...content.split("\n"));
    lines.push("");
  }
  return lines;
}

function wrapLine(line: string, width = 88): string[] {
  if (!line) return [""];
  const result: string[] = [];
  let remaining = line;
  while (remaining.length > width) {
    let split = remaining.lastIndexOf(" ", width);
    if (split < width / 2) split = width;
    result.push(remaining.slice(0, split));
    remaining = remaining.slice(split).trimStart();
  }
  result.push(remaining);
  return result;
}

const win1252: Record<number, number> = {
  0x2018: 0x91, 0x2019: 0x92, 0x201c: 0x93, 0x201d: 0x94,
  0x2013: 0x96, 0x2014: 0x97, 0x2026: 0x85, 0x20ac: 0x80,
};

function pdfLiteral(value: string): Uint8Array {
  const bytes: number[] = [];
  for (const char of value) {
    const code = char.codePointAt(0) || 0x3f;
    const byte = code <= 0xff ? code : win1252[code] ?? 0x3f;
    if (byte === 0x28 || byte === 0x29 || byte === 0x5c) bytes.push(0x5c);
    bytes.push(byte);
  }
  return Uint8Array.from(bytes);
}

function ascii(value: string): Uint8Array {
  return Uint8Array.from([...value].map((char) => char.charCodeAt(0) & 0xff));
}

function makePdf(messages: ConversationMessage[]): Uint8Array {
  const lines = transcriptLines(messages).flatMap((line) => wrapLine(line));
  const pages: string[][] = [];
  for (let i = 0; i < lines.length; i += 48) pages.push(lines.slice(i, i + 48));
  if (!pages.length) pages.push(["Curiosity Ocean", "No conversation content."]);

  const pageObjectIds = pages.map((_, index) => 4 + index * 2);
  const fontObjectId = 4 + pages.length * 2;
  const objects = new Map<number, Uint8Array>();
  objects.set(1, ascii("<< /Type /Catalog /Pages 2 0 R >>"));
  objects.set(2, ascii(`<< /Type /Pages /Kids [${pageObjectIds.map((id) => `${id} 0 R`).join(" ")}] /Count ${pages.length} >>`));
  objects.set(3, ascii("<< /Producer (Clisonix Curiosity Ocean) >>"));

  pages.forEach((pageLines, index) => {
    const pageId = pageObjectIds[index];
    const contentId = pageId + 1;
    const commands: Uint8Array[] = [ascii("BT\n/F1 11 Tf\n14 TL\n54 790 Td\n")];
    pageLines.forEach((line, lineIndex) => {
      if (lineIndex > 0) commands.push(ascii("T*\n"));
      commands.push(ascii("("), pdfLiteral(line), ascii(") Tj\n"));
    });
    commands.push(ascii("ET"));
    const stream = concatBytes(commands);
    objects.set(pageId, ascii(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 ${fontObjectId} 0 R >> >> /Contents ${contentId} 0 R >>`));
    objects.set(contentId, concatBytes([ascii(`<< /Length ${stream.length} >>\nstream\n`), stream, ascii("\nendstream")]));
  });
  objects.set(fontObjectId, ascii("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"));

  const header = ascii("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");
  const chunks: Uint8Array[] = [header];
  const offsets = [0];
  let cursor = header.length;
  for (let id = 1; id <= fontObjectId; id += 1) {
    const chunk = concatBytes([ascii(`${id} 0 obj\n`), objects.get(id)!, ascii("\nendobj\n")]);
    offsets[id] = cursor;
    chunks.push(chunk);
    cursor += chunk.length;
  }
  const xrefOffset = cursor;
  const xref = ["xref", `0 ${fontObjectId + 1}`, "0000000000 65535 f "];
  for (let id = 1; id <= fontObjectId; id += 1) {
    xref.push(`${String(offsets[id]).padStart(10, "0")} 00000 n `);
  }
  chunks.push(ascii(`${xref.join("\n")}\ntrailer\n<< /Size ${fontObjectId + 1} /Root 1 0 R /Info 3 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`));
  return concatBytes(chunks);
}

function makeDocx(messages: ConversationMessage[]): Uint8Array {
  const paragraphs = transcriptLines(messages).map((line, index) => {
    const bold = index < 2 || /^[A-Z][A-Z0-9 _-]*$/.test(line);
    const properties = bold ? "<w:rPr><w:b/></w:rPr>" : "";
    return `<w:p><w:r>${properties}<w:t xml:space="preserve">${xmlEscape(line)}</w:t></w:r></w:p>`;
  }).join("");
  const document = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>${paragraphs}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>`;
  return zip([
    {
      name: "[Content_Types].xml",
      content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>`,
    },
    {
      name: "_rels/.rels",
      content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`,
    },
    { name: "word/document.xml", content: document },
  ]);
}

function columnName(index: number): string {
  let value = index + 1;
  let result = "";
  while (value > 0) {
    const rem = (value - 1) % 26;
    result = String.fromCharCode(65 + rem) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function xlsxCell(ref: string, value: string): string {
  return `<c r="${ref}" t="inlineStr"><is><t xml:space="preserve">${xmlEscape(value)}</t></is></c>`;
}

function makeXlsx(messages: ConversationMessage[]): Uint8Array {
  const rows = [
    ["Role", "Content"],
    ...messages
      .filter((message) => String(message.content || "").trim())
      .map((message) => [
        String(message.role || "user").toUpperCase(),
        String(message.content || "")
          .replace(/\r\n/g, "\n")
          .trim(),
      ]),
  ];

  const sheetRows = rows
    .map((cells, rowIndex) => {
      const xmlCells = cells
        .map((value, cellIndex) =>
          xlsxCell(`${columnName(cellIndex)}${rowIndex + 1}`, value),
        )
        .join("");
      return `<row r="${rowIndex + 1}">${xmlCells}</row>`;
    })
    .join("");

  const worksheet = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="1" width="18" customWidth="1"/><col min="2" max="2" width="120" customWidth="1"/></cols><sheetData>${sheetRows}</sheetData></worksheet>`;
  const workbook = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Conversation" sheetId="1" r:id="rId1"/></sheets></workbook>`;

  return zip([
    {
      name: "[Content_Types].xml",
      content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>`,
    },
    {
      name: "_rels/.rels",
      content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`,
    },
    {
      name: "xl/_rels/workbook.xml.rels",
      content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>`,
    },
    { name: "xl/workbook.xml", content: workbook },
    { name: "xl/worksheets/sheet1.xml", content: worksheet },
  ]);
}

export function createConversationArtifact(
  format: LocalExportFormat,
  messages: ConversationMessage[],
): ExportArtifact {
  const stamp = new Date().toISOString().slice(0, 10);
  if (format === "pdf") {
    return {
      fileName: `curiosity-ocean-${stamp}.pdf`,
      mimeType: "application/pdf",
      bytes: makePdf(messages),
    };
  }
  if (format === "xlsx") {
    return {
      fileName: `curiosity-ocean-${stamp}.xlsx`,
      mimeType:
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      bytes: makeXlsx(messages),
    };
  }
  return {
    fileName: `curiosity-ocean-${stamp}.docx`,
    mimeType:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    bytes: makeDocx(messages),
  };
}
