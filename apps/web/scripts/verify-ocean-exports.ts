import assert from "node:assert/strict";
import { createConversationArtifact } from "../app/api/ocean/curiosity/export/export-artifacts.ts";

const messages = [
  { role: "user", content: "Analize e thelle me tekst shqip dhe Unicode: ë, ç." },
  { role: "assistant", content: "A valid answer\nwith multiple lines (and parentheses)." },
];

const pdf = createConversationArtifact("pdf", messages);
assert.equal(new TextDecoder().decode(pdf.bytes.slice(0, 8)), "%PDF-1.4");
assert.ok(pdf.bytes.length > 500);
assert.equal(pdf.mimeType, "application/pdf");

const docx = createConversationArtifact("docx", messages);
assert.deepEqual([...docx.bytes.slice(0, 4)], [0x50, 0x4b, 0x03, 0x04]);
assert.ok(docx.bytes.length > 1000);
assert.equal(
  docx.mimeType,
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
);

const xlsx = createConversationArtifact("xlsx", messages);
assert.deepEqual([...xlsx.bytes.slice(0, 4)], [0x50, 0x4b, 0x03, 0x04]);
assert.ok(xlsx.bytes.length > 900);
assert.equal(
  xlsx.mimeType,
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
);

console.log(
  `Ocean export verification passed: PDF=${pdf.bytes.length} bytes, DOCX=${docx.bytes.length} bytes, XLSX=${xlsx.bytes.length} bytes`,
);
